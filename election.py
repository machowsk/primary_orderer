import csv

DEFAULT_CSV_FILENAME = 'election2016.csv'


class State:

    totalEC = 0

    # "Enumerations" to indicate which scoring methodology to use.
    DELTA_ONLY = 1
    DELTA_AND_EC = 2
    

    methodology = DELTA_ONLY

    def __init__(self, name, dem, rep, ec):
        self.name = name
        self.dem = int(dem)
        self.rep = int(rep)
        self.delta = float(abs(self.dem - self.rep)) / float(self.dem + self.rep)
        self.ec = int(ec)


    @staticmethod
    def parseCSV(filename=DEFAULT_CSV_FILENAME):

        states = []
        State.totalEC = 0
        with open(filename, 'r') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                states.append(State(name=row['State'], dem=row['Dem'], rep=row['Rep'], ec=row['EC']))
                State.totalEC += int(row['EC'])

        return states

    def computeScore(self):

        score_scalar = 10.0
        delta_strength = 1.0 - self.delta

        if State.DELTA_ONLY == State.methodology:
            return score_scalar * delta_strength

        elif State.DELTA_AND_EC == State.methodology:
            ec_strength = float(self.ec) / float(State.totalEC) if self.ec > 0 else 0.0
            return score_scalar * (ec_strength + delta_strength)

        return 0.0

    def __str__(self):
        fullname = "{name} ({ec})".format(name=self.name, ec=self.ec)
        delta_percent = "{delta:.2f}%".format(delta=self.delta * 100.0)
        return "{fullname:<20} {score:>8.2f} {delta:>8}".format(fullname=fullname, delta=delta_percent, score=self.computeScore())

    @staticmethod
    def printHeader():
        print("{name:<20} {score:>8} {delta:>8}".format(name="NAME (EC)", score="SCORE", delta="DELTA"))
        print("_" * 38)


def processElection(filename=DEFAULT_CSV_FILENAME, methodology=State.DELTA_ONLY):

    State.methodology = methodology
    states = State.parseCSV(filename=filename)

    sortedstates = sorted(states, key=lambda s: s.computeScore(), reverse=True)

    State.printHeader()
    for state in sortedstates:
        print(state)


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser(description="Calculate an optimized order for state primaries to occur")
    parser.add_argument('--method', action='store', choices=['delta', 'delta_ec'], default='delta')
    parser.add_argument('--csv', action='store', default=DEFAULT_CSV_FILENAME)

    args = parser.parse_args()
    method = State.DELTA_ONLY
    if args.method == 'delta_ec':
        method = State.DELTA_AND_EC

    import os
    import sys
    filename = args.csv
    filename = os.path.abspath(filename)
    if not os.path.exists(filename) or not os.path.isfile(filename):
        print("{fn} doesn't seem to be a file. Exiting'".format(fn=filename))
        sys.exit(-1)

    processElection(filename=filename, methodology=method)