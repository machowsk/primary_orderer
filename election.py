import csv
from enum import IntEnum, unique

DEFAULT_CSV_FILENAME = 'election2016.csv'


class State:

    def __init__(self, nation, name, dem, rep, ec):
        self.name = name
        self.dem = int(dem)
        self.rep = int(rep)
        self.delta = float(abs(self.dem - self.rep)) / float(self.dem + self.rep)
        self.ec = int(ec)
        self.nation = nation

    def computeScore(self):

        score_scalar = 10.0
        delta_strength = 1.0 - self.delta

        if Methodology.DELTA_ONLY == self.nation.methodology:
            return score_scalar * delta_strength

        elif Methodology.DELTA_AND_EC == self.nation.methodology:
            ec_strength = float(self.ec) / float(self.nation.totalElectoralCollegeSize) if self.ec > 0 else 0.0

            # Is simply adding these two values the right thing to do? We could scale them to give more or less weight
            # to the state's size in the electoral college...
            return score_scalar * (ec_strength + delta_strength)

        return 0.0

    def __str__(self):
        fullname = "{name} ({ec})".format(name=self.name, ec=self.ec)
        delta_percent = "{delta:.2f}%".format(delta=self.delta * 100.0)
        return "{fullname:<20} {score:>8.2f} {delta:>8}".format(fullname=fullname, delta=delta_percent,
                                                                score=self.computeScore())


@unique
class Methodology(IntEnum):
    DELTA_ONLY = 1    # Only consider how close the last race was when scoring a state for the next cycle
    DELTA_AND_EC = 2  # Consider how close the last race was AND the size of the state in the Electoral College


class Nation:
    
    def __init__(self):
        
        self.totalElectoralCollegeSize = 0
        self.states = []

    def parseCSV(self, filename=DEFAULT_CSV_FILENAME):
        self.states = []
        self.totalElectoralCollegeSize = 0
        with open(filename, 'r') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                self.states.append(State(nation=self, name=row['State'], dem=row['Dem'], rep=row['Rep'], ec=row['EC']))
                self.totalElectoralCollegeSize += int(row['EC'])

    @staticmethod
    def printHeader():
        headerText = "{name:<20} {score:>8} {delta:>8}".format(name="NAME (EC)", score="SCORE", delta="DELTA")
        print(headerText)
        print("_" * len(headerText))

    def processElection(self, filename=DEFAULT_CSV_FILENAME, methodology = Methodology.DELTA_ONLY):

        self.methodology = methodology
        self.parseCSV(filename=filename)
        sortedstates = sorted(self.states, key=lambda s: s.computeScore(), reverse=True)

        Nation.printHeader()
        for state in sortedstates:
            print(state)


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser(description="Calculate an optimized order for state primaries to occur")
    parser.add_argument('--method', action='store', choices=['delta', 'delta_ec'], default='delta')
    parser.add_argument('--csv', action='store', default=DEFAULT_CSV_FILENAME)

    args = parser.parse_args()
    method = Methodology.DELTA_ONLY
    if args.method == 'delta_ec':
        method = Methodology.DELTA_AND_EC

    import os
    import sys
    filename = args.csv
    filename = os.path.abspath(filename)
    if not os.path.exists(filename) or not os.path.isfile(filename):
        print("{fn} doesn't seem to be a file. Exiting'".format(fn=filename))
        sys.exit(-1)

    Nation().processElection(filename=filename, methodology=method)
