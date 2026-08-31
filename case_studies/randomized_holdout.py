"""Case study 1: randomized customer holdout incrementality test."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("outputs/randomized_holdout"); OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)
n = 20000
treatment = rng.binomial(1, 0.5, n)
baseline = rng.normal(55, 18, n).clip(5, 150)
probability = 1 / (1 + np.exp(-(-2.15 + .018 * baseline + .22 * treatment)))
converted = rng.binomial(1, probability)
revenue = converted * rng.gamma(3.5, 24, n)
df = pd.DataFrame({"treatment": treatment, "converted": converted, "revenue": revenue})

summary = df.groupby("treatment").agg(customers=("converted","size"), conversions=("converted","sum"), conversion_rate=("converted","mean"), revenue=("revenue","sum"))
p1, p0 = summary.loc[1,"conversion_rate"], summary.loc[0,"conversion_rate"]
n1, n0 = summary.loc[1,"customers"], summary.loc[0,"customers"]
lift = p1-p0; se = np.sqrt(p1*(1-p1)/n1+p0*(1-p0)/n0); z=lift/se
ci=(lift-1.96*se,lift+1.96*se); pvalue=2*(1-norm.cdf(abs(z)))
incremental_conversions=lift*n1
incremental_revenue=incremental_conversions*(df.loc[(df.treatment==0)&(df.converted==1),"revenue"].mean())
results=pd.DataFrame([{"absolute_lift":lift,"relative_lift":lift/p0,"ci_low":ci[0],"ci_high":ci[1],"p_value":pvalue,"incremental_conversions":incremental_conversions,"incremental_revenue":incremental_revenue}])
summary.to_csv(OUT/"group_summary.csv"); results.to_csv(OUT/"incrementality_results.csv",index=False)
fig,ax=plt.subplots(figsize=(7,4)); ax.bar(["Control","Treatment"],[p0,p1],color=["#64748b","#0f766e"]); ax.set(ylabel="Conversion rate",title="Randomized holdout: observed conversion"); ax.bar_label(ax.containers[0],labels=[f"{p0:.1%}",f"{p1:.1%}"]); fig.tight_layout(); fig.savefig(OUT/"conversion_lift.png",dpi=160); plt.close(fig)
print(summary.round(4)); print(results.round(4).to_string(index=False))
