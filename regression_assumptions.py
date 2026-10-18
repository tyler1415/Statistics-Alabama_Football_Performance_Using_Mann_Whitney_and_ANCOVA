"""Check the assumptions of the home-field regression (OLS)."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson

folder = Path(__file__).parent
games = pd.read_csv(folder / "alabama_games_2007_2025.csv")  # already in date order

# Same 0/1 columns as the Excel regression (away and afternoon are the baselines)
games["home"] = (games["site"] == "home").astype(int)
games["neutral"] = (games["site"] == "neutral").astype(int)
games["morning"] = (games["kickoff_ct"] < 12).astype(int)
games["night"] = (games["kickoff_ct"] >= 17).astype(int)

model = smf.ols("margin ~ home + neutral + morning + night + opp_ranked + non_conf", data=games).fit()
resid = model.resid
fitted = model.fittedvalues
print(f"Model: R-squared = {model.rsquared:.3f}, home effect = {model.params['home']:+.2f}\n")

# 1. LINEARITY / ADDITIVITY
# Every X is 0/1, so a straight line always fits each one exactly. The real question is
# whether effects simply add up. Test one interaction: is home field worth more vs ranked teams?
inter = smf.ols("margin ~ home * opp_ranked + neutral + morning + night + non_conf", data=games).fit()
print("1. Additivity (home x ranked interaction)")
print(f"   interaction = {inter.params['home:opp_ranked']:+.2f} points, p = {inter.pvalues['home:opp_ranked']:.3f}")
print("   -> p > 0.05 means no evidence that effects fail to add up\n")

# 2. INDEPENDENCE: are back-to-back games' errors related?
dw = durbin_watson(resid)
print("2. Independence (Durbin-Watson, games in date order)")
print(f"   DW = {dw:.2f}   (2 = none; below ~1.5 or above ~2.5 is a concern)\n")

# 3. EQUAL VARIANCE: are the errors about the same size for every prediction?
bp_stat, bp_p, _, _ = het_breuschpagan(resid, model.model.exog)
print("3. Equal variance (Breusch-Pagan)")
print(f"   p = {bp_p:.3f}   (p > 0.05 means no evidence of unequal variance)\n")

# 4. NORMAL ERRORS: do the residuals form a bell curve?
sw_stat, sw_p = stats.shapiro(resid)
print("4. Normal residuals (Shapiro-Wilk)")
print(f"   W = {sw_stat:.3f}, p = {sw_p:.3f}   skew = {stats.skew(resid):.2f}, excess kurtosis = {stats.kurtosis(resid):.2f}")
print("   -> p > 0.05 and skew/kurtosis near 0 means roughly normal\n")

# 5. MULTICOLLINEARITY: are any X columns too closely related to each other?
X = model.model.exog
names = model.model.exog_names
print("5. Multicollinearity (VIF; under 5 is fine, over 10 is a problem)")
for i, name in enumerate(names):
    if name != "Intercept":
        print(f"   {name:11s} VIF = {variance_inflation_factor(X, i):.2f}")
print()

# 6. INFLUENTIAL GAMES: does any single game pull the results around?
infl = model.get_influence()
cooks = infl.cooks_distance[0]
student = infl.resid_studentized_external
cutoff = 4 / len(games)
flagged = games.assign(cooks=cooks, studentized=student)[(cooks > cutoff) | (np.abs(student) > 3)]
print(f"6. Influential games (Cook's distance > {cutoff:.3f} or |studentized residual| > 3)")
print(f"   {len(flagged)} games flagged; largest Cook's distance = {cooks.max():.3f} (over 1 is a serious concern)")
print(flagged[["season", "opponent", "site", "margin", "cooks", "studentized"]]
      .sort_values("cooks", ascending=False).head(8).round(3).to_string(index=False))
robust = smf.ols(model.model.formula, data=games[cooks <= cutoff]).fit()
print(f"   home effect without flagged games: {robust.params['home']:+.2f} (vs {model.params['home']:+.2f} with them)\n")

# PLOTS
fig, ax = plt.subplots(2, 2, figsize=(11, 8))
ax[0, 0].scatter(fitted, resid, alpha=0.5, s=14, color="#9E1B32")
ax[0, 0].axhline(0, color="gray", lw=1)
ax[0, 0].set(title="Residuals vs predicted (want: even band, no funnel)", xlabel="Predicted margin", ylabel="Residual")
sm.qqplot(resid, line="s", ax=ax[0, 1])
ax[0, 1].set_title("Q-Q plot of residuals (want: points on the line)")
ax[1, 0].hist(resid, bins=25, color="#9E1B32", alpha=0.7, edgecolor="white")
ax[1, 0].set(title="Histogram of residuals (want: bell shape)", xlabel="Residual")
ax[1, 1].plot(resid.to_numpy(), marker="o", ms=3, lw=0.6, color="#555")
ax[1, 1].axhline(0, color="gray", lw=1)
ax[1, 1].set(title="Residuals in game order (want: no waves or runs)", xlabel="Game number (2007 to 2025)", ylabel="Residual")
fig.tight_layout()
out = folder / "figures" / "regression_assumptions.png"
out.parent.mkdir(exist_ok=True)
fig.savefig(out, dpi=150)
print(f"Plots saved to {out}")
