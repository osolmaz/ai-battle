# Trace

## Cells
- x_outer: the outer x cell
- y_f: created inside maker(2) call, shared by f, g, h closures

## maker = proc(seed) that creates y=seed, returns proc(delta) capturing x_outer, y

## maker(2):
- seed=2, y_f=2
- returns proc(delta){x=x+delta; y=y+x; return proc(k){y=y+k; x=x+y; return x+y}}
- f captures x_outer, y_f

State: x_outer=1, y_f=2

## f(3):
- delta=3
- x_outer = 1+3 = 4
- y_f = 2+4 = 6
- returns proc(k){y_f=y_f+k; x_outer=x_outer+y_f; return x_outer+y_f}
- g captures x_outer, y_f

State: x_outer=4, y_f=6

## print(x) → x_outer = 4  → OUTPUT: 4

## let x = 100 (x_inner=100, shadows x_outer in lexical scope)

## g(4):
- k=4
- y_f = 6+4 = 10
- x_outer = 4+10 = 14
- return 14+10 = 24

State: x_outer=14, y_f=10

## print(g(4)) → OUTPUT: 24

## print(x) → x_inner = 100  → OUTPUT: 100

## f(1):
- delta=1
- x_outer = 14+1 = 15
- y_f = 10+15 = 25
- returns proc(k) capturing same x_outer, y_f
- h captures x_outer, y_f

State: x_outer=15, y_f=25

## h(0):
- k=0
- y_f = 25+0 = 25
- x_outer = 15+25 = 40
- return 40+25 = 65

State: x_outer=40, y_f=25

## print(h(0)) → OUTPUT: 65

## End let x=100 block, x_inner discarded

## print(x) → x_outer = 40  → OUTPUT: 40

## g(0):
- k=0
- y_f = 25+0 = 25
- x_outer = 40+25 = 65
- return 65+25 = 90

## print(g(0)) → OUTPUT: 90

## Final: 4, 24, 100, 65, 40, 90
