#!/usr/bin/env python3
"""Build the minimal Apple Device Tree that the M30LTE xnu needs to boot.

Only values supported by the saved M30 tree are emitted. Usage:
mkadt.py OUT.adt [--dump] [--qemu]
"""
import os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adt  # noqa: E402

# Kernel-managed RAM (from live DT: memory@80000000 = 0x3DA00000 @ 0x80000000)
# Use Bank 0 only; other banks are noncontiguous or above the current loader model.
PHYS_BASE = 0x80000000
MEM_SIZE = 0x3DA00000  # 986 MB from first bank
SOC_BASE = 0x01000000

# Exynos 7904 interrupt-controller@123001000 raw reg tuples:
# distributor-like window 0x12301000/0x1000 and CPU-interface-like
# window 0x12302000/0x1000. Do not synthesize a GICv3 redistributor.
GICD, GICD_SIZE = 0x12301000, 0x1000
GICC, GICC_SIZE = 0x12302000, 0x1000
FB, FB_SIZE = 0xEC000000, 0x1400000
FB_W, FB_H, FB_STRIDE = 1080, 2340, 1080 * 4
# M30 uses eMMC, not UFS
EMMC, EMMC_SIZE = 0x13500000, 0x2000  # first raw DT reg tuple
VTIMER_INTID = 27  # PPI 11 -> GIC INTID 27
# QEMU virt (-M virt,gic-version=3 -cpu cortex-a76)
QEMU_GICD, QEMU_GICR = 0x08000000, 0x080a0000
QEMU_VTIMER_INTID = 27


D22AP_ADT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../research/ipsw-x/d22ap.adt')


def d22ap_product(path=D22AP_ADT):
    if not os.path.exists(path):
        print(f'warning: {path} missing, no /product node', file=sys.stderr)
        return None
    root, _ = adt.parse(open(path, 'rb').read())
    for c in root.children:
        if dict((k, v) for k, f, v in c.props).get('name') == b'product\0':
            return [(k, v) for k, f, v in c.props if not f and k not in ('name', 'AAPL,phandle')]
    raise SystemExit(f'{path}: no /product node')


u32 = lambda *v: struct.pack('<%dI' % len(v), *v)
u64 = lambda *v: struct.pack('<%dQ' % len(v), *v)
cstr = lambda s: s.encode() + b'\0'


def node(name, props=(), children=()):
    n = adt.Node()
    n.props = [('name', 0, cstr(name))] + [(k, 0, v) for k, v in props]
    n.children = list(children)
    return n


def build(seed=None, qemu=False):
    phys_base, mem_size = PHYS_BASE, MEM_SIZE
    gicd, gicc = (QEMU_GICD, QEMU_GICR) if qemu else (GICD, GICC)
    seed = seed if seed is not None else os.urandom(64)
    phandle = iter(range(1, 1000))
    ph = lambda: ('AAPL,phandle', u32(next(phandle)))

    chosen = node('chosen', [
        ph(),
        ('dram-base', u64(phys_base)),
        ('dram-size', u64(mem_size)),
        ('random-seed', seed),
        ('debug-enabled', u32(1)),
        ('firmware-version', cstr('m30lte-shim')),
        ('system-firmware-version', cstr('m30lte-shim')),
    ], [node('memory-map', [ph()]),
        node('asmb', [ph()])])

    cpu_nodes = []
    raw_cpus = [(0, 'arm,cortex-a73', 6), (1, 'arm,cortex-a73', 7),
                (0x100, 'arm,cortex-a53', 0), (0x101, 'arm,cortex-a53', 1),
                (0x102, 'arm,cortex-a53', 2), (0x103, 'arm,cortex-a53', 3),
                (0x200, 'arm,cortex-a53', 4), (0x201, 'arm,cortex-a53', 5)]
    if qemu:
        raw_cpus = [(0, 'arm,cortex-a53', 0)]
    for mpidr, compatible, logical_id in raw_cpus:
        cpu_nodes.append(node(f'cpu@{mpidr:x}', [
            ph(),
            ('device_type', cstr('cpu')),
            ('compatible', cstr(compatible) + cstr('arm,armv8')),
            ('reg', u64(mpidr)),
            ('logical-id', u32(logical_id)),
            ('enable-method', cstr('psci')),
        ]))
    cpus = node('cpus', [ph(), ('#address-cells', u32(2)),
                         ('#size-cells', u32(0))], cpu_nodes)

    # GICv2 node (from live DT: compatible="arm,cortex-a15-gic")
    gic = node('gic', [
        ph(),
        ('compatible', cstr('arm,cortex-a15-gic')),
        ('interrupt-controller', b''),
        ('virtual-timer-intid', u32(QEMU_VTIMER_INTID if qemu else VTIMER_INTID)),
        ('reg', u64(gicd - SOC_BASE, GICD_SIZE, gicc - SOC_BASE, GICC_SIZE)),
    ])
    arm_io = node('arm-io', [
        ph(),
        ('device_type', cstr('m30lte-io')),
        ('compatible', cstr('m30lte-io') + cstr('arm-io')),
        ('#address-cells', u32(2)),
        ('#size-cells', u32(2)),
        ('ranges', u64(0, SOC_BASE, 0x100000000 - SOC_BASE)),
    ], [gic,
        node('wdt', [ph(), ('no-pmu', u32(1))]),
        node('disp0', [
            ph(),
            ('device_type', cstr('display-subsystem')),
            ('compatible', cstr('m30lte,display')),
            ('canvas-width', u32(1080)),
            ('canvas-height', u32(2340)),
        ])])

    fbcon = node('m30lte-fbcon', [
        ph(),
        ('reg', u64(FB, FB_SIZE)),
        ('width', u32(FB_W)),
        ('height', u32(FB_H)),
        ('stride', u32(FB_STRIDE)),
    ])

    # M30 uses eMMC (DWMMC), not UFS
    emmc = node('m30lte-emmc', [
        ph(),
        ('compatible', cstr('samsung,dw-mshc')),
        ('reg', u64(EMMC, EMMC_SIZE)),
    ])

    defaults = node('defaults', [ph()])

    buttons = node('buttons', [
        ph(),
        ('button-names', cstr('volup') + cstr('voldown') + cstr('hold')),
        ('home-button-type', u32(2)),
        ('opposed-power-vol-buttons', u32(1)),
    ])

    product_props = d22ap_product()
    product = [node('product', [ph()] + product_props)] if product_props else []

    return node('device-tree', [
        ph(),
        ('compatible', cstr('samsung,m30lte') + cstr('samsung,exynos7904') + cstr('AppleARM')),
        ('model', cstr('samsung,m30lte')),
        ('target-type', cstr('SAMSUNG')),
        ('target-sub-type', cstr('M30LTE')),
        ('manufacturer', cstr('Samsung Electronics Co., Ltd.')),
        ('#address-cells', u32(2)),
        ('#size-cells', u32(2)),
    ], [chosen, defaults, cpus, arm_io, fbcon, buttons] + product + ([] if qemu else [emmc]))


if __name__ == '__main__':
    root = build(qemu='--qemu' in sys.argv)
    blob = adt.serialize(root)
    # Pad the ADT to exactly M30_ADT_EXPECTED_SIZE (0x27c4 = 10180 bytes)
    # The kernel expects exactly this size for the embedded ADT.
    if len(blob) < 0x27c4:
        blob += b"\x00" * (0x27c4 - len(blob))
    elif len(blob) > 0x27c4:
        raise ValueError(f"ADT too large: {len(blob)} > 0x27c4")
    open(sys.argv[1], 'wb').write(blob)
    if '--dump' in sys.argv:
        adt.dump(adt.parse(blob)[0])
    print(f'{sys.argv[1]}: {len(blob)} bytes', file=sys.stderr)
