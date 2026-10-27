/*
 * M30 LTE: Exynos 7885 eMMC driver (DWMC host controller).
 *
 * Runs with the MMU off (all memory Device, so DMA is coherent with no cache
 * maintenance). Reads the eMMC device ABL booted from and verifies we can talk
 * to it. Only read operations: nothing is ever written to the device.
 *
 * Register layout: Synopsys DesignWare Mobile Storage Host Controller.
 */
#include <stdint.h>
#include "console.h"
#include "emmc.h"

/* Exynos 7885 DWMC host controller (from /proc/device-tree/dwmmc0@13500000) */
#define EMMC_BASE	0x0000000013500000UL

/* DW-MMC register offsets */
#define SDR0			0x00	/* SD/MMC control register 0 */
#define SDR1			0x04	/* SD/MMC control register 1 */
#define SDR2			0x08	/* SD/MMC control register 2 */
#define SDR3			0x0C	/* SD/MMC control register 3 */
#define SDR4			0x0C	/* SD/MMC control register 4 */
#define SDIER			0x14	/* Interrupt enable register */
#define SDICR			0x18	/* Interrupt clear register */
#define SDISR			0x1C	/* Interrupt status register */
#define SDSTA			0x20	/* Status register */
#define SDCMD			0x24	/* Command register */
#define SDARG			0x28	/* Argument register */
#define SDCMD0			0x2C	/* Command 0 register */
#define SDCMD1			0x30	/* Command 1 register */
#define SDCMD2			0x34	/* Command 2 register */
#define SDCMD3			0x38	/* Command 3 register */
#define SDCMD4			0x3C	/* Command 4 register */
#define SDCMD5			0x3C	/* Command 5 register */
#define SDRESP0			0x3C	/* Response register 0 */
#define SDRESP1			0x40	/* Response register 1 */
#define SDRESP2			0x44	/* Response register 2 */
#define SDRESP3			0x48	/* Response register 3 */
#define SDTXDATA			0x50	/* Transmit data register */
#define SDRXDATA			0x54	/* Receive data register */
#define SDBSIZ			0x58	/* Block size register */
#define SDBLKCNT			0x5C	/* Block count register */
#define SDIFCTRL			0x60	/* Interface control register */
#define SDCMDARG			0x64	/* Command argument register */
#define SDCMDSTAT			0x68	/* Command status register */

/* SDMMC_CTL bits */
#define SDC_ENABLE		(1u << 0)
#define SDC_CARD_DETECT		(1u << 1)
#define SDC_CLK_EN		(1u << 2)
#define SDC_CLK_FREQ_SHIFT	(3)
#define SDC_CLK_FREQ_MASK	(0x1f << 3)
#define SDC_BUS_WIDTH_SHIFT	(8)
#define SDC_BUS_WIDTH_MASK	(0x3 << 8)

/* SDMMC_STA bits */
#define SD_STA_CC			(1u << 0)	/* Command complete */
#define SD_STA_CTO			(1u << 1)	/* Command timeout */
#define SD_STA_CRC			(1u << 2)	/* Command CRC error */
#define SD_STA_TC			(1u << 3)	/* Transfer complete */
#define SD_STA_TTO			(1u << 4)	/* Transfer timeout */
#define SD_STA_TCR			(1u << 5)	/* Transfer CRC error */
#define SD_STA_RTO			(1u << 6)	/* Read timeout */
#define SD_STA_RCR			(1u << 7)	/* Read CRC error */
#define SD_STA_TBC			(1u << 8)	/* Transfer complete (block) */
#define SD_STA_ALL_ERRORS		(SD_STA_CRC | SD_STA_CTO | SD_STA_TCR | SD_STA_TTO | SD_STA_RTO | SD_STA_RCR)

/* SDMMC_CMD bits */
#define SDC_CMD_INDEX_SHIFT	(0)
#define SDC_CMD_INDEX_MASK	(0x3f << 0)
#define SDC_CMD_TYPE_SHIFT	(6)
#define SDC_CMD_TYPE_MASK	(0x3 << 6)
#define SDC_CMD_WAIT_RESP_SHIFT	(8)
#define SDC_CMD_WAIT_RESP_MASK	(0x3 << 8)
#define SDC_CMD_DATA_EXPECTED	(1u << 10)
#define SDC_CMD_READ			(1u << 11)
#define SDC_CMD_AUTO_STOP		(1u << 12)
#define SDC_CMD_UPDATE_CLOCK	(1u << 13)
#define SDC_CMD_WRITE			(1u << 14)

/* Command types */
#define CMD_TYPE_NORMAL		0
#define CMD_TYPE_SUSPEND	1
#define CMD_TYPE_RESUME		2
#define CMD_TYPE_ABORT		3

/* Response types */
#define CMD_RESP_NONE		0
#define CMD_RESP_SHORT		1
#define CMD_RESP_LONG		2
#define CMD_RESP_SHORT_BUSY	3

/* CMD indices */
#define CMD0_GO_IDLE_STATE		0
#define CMD1_SEND_OP_COND		1
#define CMD2_ALL_SEND_CID		2
#define CMD3_SEND_RELATIVE_ADDR		3
#define CMD4_SET_DSR			4
#define CMD5_SLEEP_AWAKE		5
#define CMD6_SWITCH			6
#define CMD7_SELECT_DESELECT		7
#define CMD8_SEND_EXT_CSD		8
#define CMD9_SEND_CSD			9
#define CMD10_SEND_CID			10
#define CMD12_STOP_TRANSMISSION		12
#define CMD13_SEND_STATUS		13
#define CMD15_SEND_STATUS			15
#define CMD16_SET_BLOCKLEN		16
#define CMD17_READ_SINGLE_BLOCK		17
#define CMD18_READ_MULTIPLE_BLOCK		18
#define CMD24_WRITE_BLOCK			24
#define CMD25_WRITE_MULTIPLE_BLOCK	25
#define CMD27_PROGRAM_CSD			27
#define CMD32_ERASE_WR_BLK_START		32
#define CMD33_ERASE_WR_BLK_END		33
#define CMD38_ERASE			38
#define CMD42_LOCK_UNLOCK		42
#define CMD55_APP_CMD			55
#define CMD56_GENERIC			56

/* Card status bits */
#define CARD_STATE_MASK		(0xf << 9)
#define CARD_STATE_READY		(0x3 << 9)
#define CARD_STATE_IDENT		(0x2 << 9)
#define CARD_STATE_STBY		(0x3 << 9)
#define CARD_STATE_TRAN		(0x4 << 9)
#define CARD_STATE_DATA		(0x5 << 9)
#define CARD_STATE_RCV		(0x6 << 9)
#define CARD_STATE_DATA		(0x7 << 9)
#define CARD_STATE_PRG		(0x7 << 9)
#define CARD_STATE_DIS		(0x8 << 9)

static inline uint32_t emmc_rd(uint32_t off)
{
	return *(volatile uint32_t *)(EMMC_BASE + off);
}

static inline void emmc_wr(uint32_t off, uint32_t v)
{
	*(volatile uint32_t *)(EMMC_BASE + off) = v;
}

static void emmc_delay_ms(unsigned ms)
{
	uint64_t end = rsr("cntpct_el0") + rsr("cntfrq_el0") / 1000 * ms;
	while (rsr("cntpct_el0") < end)
		;
}

/* Wait for command complete */
static int emmc_wait_cmd(int timeout_ms)
{
	uint64_t end = rsr("cntpct_el0") + rsr("cntfrq_el0") / 1000 * timeout_ms;
	while (rsr("cntpct_el0") < end) {
		uint32_t sta = emmc_rd(SDSTA);
		if (sta & SD_STA_CC) {
			emmc_wr(SDICR, SD_STA_CC);	/* clear */
			return 0;
		}
		if (sta & SD_STA_CRC) {
			emmc_wr(SDICR, SD_STA_CRC);
			return -1;
		}
		if (sta & SD_STA_CTO) {
			emmc_wr(SDICR, SD_STA_CTO);
			return -2;
		}
	}
	return -3;	/* timeout */
}

/* Wait for transfer complete */
static int emmc_wait_xfer(int timeout_ms)
{
	uint64_t end = rsr("cntpct_el0") + rsr("cntfrq_el0") / 1000 * timeout_ms;
	while (rsr("cntpct_el0") < end) {
		uint32_t sta = emmc_rd(SDSTA);
		if (sta & SD_STA_TC) {
			emmc_wr(SDICR, SD_STA_TC);
			return 0;
		}
		if (sta & SD_STA_TCR) {
			emmc_wr(SDICR, SD_STA_TCR);
			return -1;
		}
		if (sta & SD_STA_TTO) {
			emmc_wr(SDICR, SD_STA_TTO);
			return -2;
		}
	}
	return -3;	/* timeout */
}

/* Send a command with no data */
static int emmc_cmd(u32 cmd, u32 arg, u32 resp_type)
{
	u32 reg = (cmd & SDC_CMD_INDEX_MASK) |
		  (SDC_CMD_TYPE_NORMAL << SDC_CMD_TYPE_SHIFT) |
		  (resp_type << SDC_CMD_WAIT_RESP_SHIFT);
	emmc_wr(SDCMDARG, arg);
	emmc_wr(SDCMD, reg);
	return emmc_wait_cmd(1000);
}

/* Send command and read response */
static int emmc_cmd_resp(u32 cmd, u32 arg, u32 resp_type, u32 *resp)
{
	int ret = emmc_cmd(cmd, arg, resp_type);
	if (ret != 0)
		return ret;
	if (resp_type == CMD_RESP_SHORT) {
		*resp = emmc_rd(SDRESP0);
	} else if (resp_type == CMD_RESP_LONG) {
		resp[0] = emmc_rd(SDRESP0);
		resp[1] = emmc_rd(SDRESP1);
		resp[2] = emmc_rd(SDRESP2);
		resp[3] = emmc_rd(SDRESP3);
	}
	return 0;
}

/* Send a read command and read data */
static int emmc_read_blocks(u32 block, u8 *buf, u32 count)
{
	int ret;
	u32 sta;

	/* Set block count */
	emmc_wr(SDBLKCNT, count);
	/* Set block size */
	emmc_wr(SDBSIZ, 512);

	/* Send READ_MULTIPLE_BLOCK */
	ret = emmc_cmd(CMD18_READ_MULTIPLE_BLOCK, block * 512,
			CMD_RESP_SHORT | SDC_CMD_DATA_EXPECTED |
			SDC_CMD_READ | SDC_CMD_AUTO_STOP);
	if (ret != 0)
		return ret;

	/* Wait for transfer complete */
	ret = emmc_wait_xfer(5000);
	if (ret != 0)
		return ret;

	/* Read data (simplified - for production we'd use DMA) */
	/* For now just wait and report */
	sta = emmc_rd(SDSTA);
	emmc_wr(SDICR, sta & SD_STA_ALL_ERRORS);

	return sta & SD_STA_ALL_ERRORS ? -1 : 0;
}

void test_emmc(void)
{
	u32 resp[4];
	int ret;

	con_str("EMMC", "probe");
	con_skip();

	/* Enable controller */
	emmc_wr(SDCMDARG, 0);
	emmc_wr(SDCMD, SDC_CMD_TYPE_NORMAL << SDC_CMD_TYPE_SHIFT);
	emmc_wr(SDCMDARG, 0);
	emmc_wr(SDCMD, (SDC_CMD_TYPE_NORMAL << SDC_CMD_TYPE_SHIFT) | SDC_CMD_UPDATE_CLOCK);
	emmc_wr(SDCMDARG, SDC_CMD_TYPE_NORMAL << SDC_CMD_TYPE_SHIFT | SDC_CMD_ENABLE);
	emmc_wr(SDCMD, SDC_CMD_TYPE_NORMAL << SDC_CMD_TYPE_SHIFT | SDC_CMD_ENABLE | SDC_CMD_UPDATE_CLOCK);
	emmc_delay_ms(10);

	/* CMD0: GO_IDLE_STATE */
	ret = emmc_cmd(CMD0_GO_IDLE_STATE, 0, CMD_RESP_NONE);
	con_hex2("EMMC", "CMD0=", ret, 0);
	if (ret != 0) {
		con_str("EMMC", "CMD0 failed");
		con_skip();
		return;
	}

	/* CMD1: SEND_OP_COND */
	ret = emmc_cmd(CMD1_SEND_OP_COND, 0x40ff8000, CMD_RESP_SHORT);
	con_hex2("EMMC", "CMD1=", ret, 0);
	if (ret != 0) {
		con_str("EMMC", "CMD1 failed");
		con_skip();
		return;
	}
	emmc_rd(SDRESP0); /* OCR */

	/* CMD2: ALL_SEND_CID */
	ret = emmc_cmd(CMD2_ALL_SEND_CID, 0, CMD_RESP_LONG);
	con_hex2("EMMC", "CMD2=", ret, 0);
	if (ret != 0) {
		con_str("EMMC", "CMD2 failed");
		con_skip();
		return;
	}

	/* CMD3: SEND_RELATIVE_ADDR */
	ret = emmc_cmd(CMD3_SEND_RELATIVE_ADDR, 0, CMD_RESP_SHORT);
	con_hex2("EMMC", "CMD3=", ret, 0);
	if (ret != 0) {
		con_str("EMMC", "CMD3 failed");
		con_skip();
		return;
	}
	u32 rca = emmc_rd(SDRESP0) >> 16;
	con_hex2("EMMC", "RCA=", rca, 0);

	/* CMD9: SEND_CSD */
	ret = emmc_cmd(CMD9_SEND_CSD, rca << 16, CMD_RESP_LONG);
	con_hex2("EMMC", "CMD9=", ret, 0);

	/* CMD7: SELECT_DEVICE */
	ret = emmc_cmd(CMD7_SELECT_DESELECT, rca << 16, CMD_RESP_SHORT);
	con_hex2("EMMC", "CMD7=", ret, 0);
	if (ret != 0) {
		con_str("EMMC", "CMD7 failed");
		con_skip();
		return;
	}

	/* CMD16: SET_BLOCKLEN */
	ret = emmc_cmd(CMD16_SET_BLOCKLEN, 512, CMD_RESP_SHORT);
	con_hex2("EMMC", "CMD16=", ret, 0);
	if (ret != 0) {
		con_str("EMMC", "CMD16 failed");
		con_skip();
		return;
	}

	con_str("EMMC", "OK");
	con_skip();
}