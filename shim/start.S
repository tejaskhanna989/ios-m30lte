/*
 * m30 boot shim entry: _start at offset 0 so ABL can jump directly.
 * No branch indirection - _start IS the entry point.
 * Draw RED on screen immediately, then hang.
 */
	.section .text.head, "ax"
	.globl _start
_start:
	/* Draw RED at fb 0xec000000 immediately */
	movz	x1, #0x0000
	movk	x1, #0xec00, lsl #16	/* x1 = 0xec000000 */
	movz	w2, #0xffff
	movk	w2, #0xff00, lsl #16	/* w2 = 0xFFFF0000 = RED (BGRA) */
	movz	x3, #0x1000			/* 4096 dwords */
1:	str	w2, [x1], #4
	subs	x3, x3, #1
	b.ne	1b

	/* Also draw GREEN at 0x9c000000 as fallback */
	movz	x1, #0x0000
	movk	x1, #0x9c00, lsl #16	/* x1 = 0x9c000000 */
	movz	w2, #0xff00
	movk	w2, #0xff00, lsl #16	/* w2 = 0xFF00FF00 = GREEN */
	movz	x3, #0x1000
2:	str	w2, [x1], #4
	subs	x3, x3, #1
	b.ne	2b

	/* Hang forever */
3:	wfe
	b	3b

	/* Exception vectors */
	.balign	0x800
	.globl vectors
vectors:
	.balign	0x80
	b	exc_common
	.rept	15
	.balign	0x80
	b	exc_common
	.endr

exc_common:
3:	wfe
	b	3b
