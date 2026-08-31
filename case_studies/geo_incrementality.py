"""Case study 2: geo incrementality with matched control markets."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT=Path("outputs/geo_incrementality"); OUT.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(7); weeks=np.arange(1,25); post=weeks>16
control=1000+12*weeks+70*np.sin(weeks/2.8)+rng.normal(0,25,len(weeks))
treated=1.12*control+45+rng.normal(0,30,len(weeks)); treated[post]+=165
df=pd.DataFrame({"week":weeks,"post":post,"control_sales":control,"treated_sales":treated})
pre=df[~df.post]; slope,intercept=np.polyfit(pre.control_sales,pre.treated_sales,1)
df["counterfactual_sales"]=slope*df.control_sales+intercept
df["incremental_sales"]=np.where(df.post,df.treated_sales-df.counterfactual_sales,np.nan)
effect=df.loc[df.post,"incremental_sales"]; test=ttest_1samp(effect,0)
summary=pd.DataFrame([{"incremental_sales":effect.sum(),"average_weekly_lift":effect.mean(),"relative_lift":effect.sum()/df.loc[df.post,"counterfactual_sales"].sum(),"p_value":test.pvalue}])
df.to_csv(OUT/"weekly_geo_results.csv",index=False); summary.to_csv(OUT/"geo_test_summary.csv",index=False)
fig,ax=plt.subplots(figsize=(9,5)); ax.plot(df.week,df.treated_sales,label="Treated market",color="#0f766e",lw=2.5); ax.plot(df.week,df.counterfactual_sales,label="Estimated counterfactual",color="#d97706",ls="--",lw=2.5); ax.axvline(16.5,color="#64748b",ls=":"); ax.fill_between(df.week,df.treated_sales,df.counterfactual_sales,where=df.post,color="#0f766e",alpha=.18,label="Incremental sales"); ax.set(xlabel="Week",ylabel="Sales",title="Geo experiment: treated market vs counterfactual"); ax.legend(); fig.tight_layout(); fig.savefig(OUT/"geo_incrementality.png",dpi=160); plt.close(fig)
print(summary.round(3).to_string(index=False))
