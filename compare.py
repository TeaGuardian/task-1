import argparse
import re
import ast
import astunparse


class Progress:
    def __init__(self, name, maxx, step=1):
        self.ma, self.st, self.no, self.la, self.name = maxx, step, 0, 0, name

    def update(self):
        self.no += 1
        rez = int(self.no / self.ma * 100)
        if rez >= self.la + self.st:
            self.la = rez
            print(f"{self.name}: {rez}%..")


def distance(a, b):
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]


def concentrate(lif):
    rez = {}
    for i in range(len(lif)):
        if lif[i] == "as":
            rez[lif[i + 1].rstrip(",")] = lif[i - 1]
    return rez


def normilize(di, line):
    if all(map(lambda x: x not in line, di.keys())):
        return line
    for i in di.keys():
        if i == di[i]:
            continue
        while i + "." in line or i + "(" in line:
            g = [m.start() for m in re.finditer(i, line)][0]
            if g + len(i) < len(line):
                if line[g + len(i)] in [".", "("]:
                    line = line[:g] + di[i] + line[g + len(i):]
    return line


def proplot(patch):
    outtext, tochange = [], {}
    print(f"reading {patch}...")
    with open(file=patch, mode="r") as file:
        rez = astunparse.unparse(ast.parse(file.read())).split('\n')
    for i in rez:
        """пропускаем комментарии"""
        if i.lstrip()[:1] in ("'", '"'):
            continue
        """приводим импорты к единому виду"""
        if " as " in i and "import " in i:
            tochange = {**tochange, **concentrate(i.split())}
        else:
            outtext.append(normilize(tochange, i))
    return outtext


def test(inp, rez):
    text1, text2 = proplot(inp), proplot(rez)
    if len(text2) > len(text1):
        text2, text1 = text1, text2
    sameidex, lendist = {}, len("".join(text1) + "".join(text2))
    pro = Progress(f"checking {inp} -> {rez}", len(text1), 10)
    su = 0
    for i in text1:
        pro.update()
        maxs, maxi = None, -1
        for j in range(len(text2)):
            if j in sameidex.keys():
                continue
            dis = distance(i, text2[j])
            if maxs is None:
                maxs, maxi = dis, j
            elif dis < maxs:
                maxs, maxi = dis, j
        if maxi >= 0:
            sameidex[maxi] = maxs
        else:
            su += len(i)
    for g in sameidex.keys():
        su += sameidex[g]
    print(f"{inp} and {rez} same on {round(1 - su / lendist, 9) * 100}%")
    return round(1 - su / lendist, 7)


def tryf(patch):
    try:
        with open(patch, mode="r") as f:
            pass
    except Exception as ex:
        print(f"problems with {patch}: {ex}")
        return False
    return True


def main(inputs, out):
    rez = []
    if not tryf(inputs):
        print("FATAL WARNING")
        return False
    with open(inputs, mode="r") as file:
        need = map(lambda x: x.rstrip("\n").split(), file.readlines())
    for inp, ou in need:
        if not tryf(inp) or not tryf(ou):
            print("FATAL WARNING")
            return False
        rez.append(test(inp, ou))
    with open(out, mode="a+") as fi:
        fi.writelines(list(map(lambda d: f"{d}\n", rez)))


parser = argparse.ArgumentParser(description='files to check')
parser.add_argument('indir', type=str, help='Input dir')
parser.add_argument('outdir', type=str, help='Output dir')
args = parser.parse_args()
print(f"Searching files in:{args.indir} out:{args.outdir}")
main(args.indir, args.outdir)
