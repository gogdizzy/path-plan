from sympy import symbols, Eq, solve, Rational

def calc2(pat1, pat2):

    # 定义符号变量

    p, p0, p1, pat1_2, pat2_2 = symbols('p p0 p1 pat1_2 pat2_2')

    pat1_2_str = pat1[:2]
    pat2_2_str = pat2[:2]

    d = dict()
    d[pat1] = 1
    d[pat2] = 0
    d[pat1_2_str] = pat1_2
    if pat1_2_str != pat2_2_str:
        d[pat2_2_str] = pat2_2
    d['0'] = p0
    d['1'] = p1

    def getEq(sym, str, d):

        c = Rational(1, 2)
        sa0 = str + '0'
        sa1 = str + '1'
        sym1 = None
        sym2 = None
        for st in range(len(sa0)):
            if sym1 is None:
                sym1 = d.get(sa0[st:], None)
            if sym2 is None:
                sym2 = d.get(sa1[st:], None)

        return Eq(sym, c * sym1 + c * sym2)


    eqs = []

    eqs.append(getEq(p, '', d))
    eqs.append(getEq(p0, '0', d))
    eqs.append(getEq(p1, '1', d))
    eqs.append(getEq(pat1_2, pat1_2_str, d))
    if pat1_2_str != pat2_2_str:
        eqs.append(getEq(pat2_2, pat2_2_str, d))
        return solve(eqs, (p, p0, p1, pat1_2, pat2_2))

    # print(eqs)

    return solve(eqs, (p, p0, p1, pat1_2))


# 打印结果
for x in range(4):
    for y in range(8):
        if x == y:
            continue
        xx = format(x, '03b')
        yy = format(y, '03b')
        print(xx, yy, calc2(xx, yy))

