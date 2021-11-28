import pandas as pd
import pickle
import os


def dbInit(db):
    d= dict(
        data=dict(),
        ref=dict(),
        analysis=dict()
            )
    pickle.dump(d, open(os.path.join(db + ".p"), "wb"))

def formatDf(data):
    a = data.copy()
    df = pd.DataFrame(a) \
        .to_html(classes='table table-striped sortable', index=False, border=0, justify="left")
    return df