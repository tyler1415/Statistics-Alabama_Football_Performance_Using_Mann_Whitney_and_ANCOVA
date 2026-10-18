# Alabama Football Performance Using Mann-Whitney and ANCOVA

Does Alabama football perform differently depending on when and where it plays? This project tests whether Alabama's point margin differs between home and away games, and between morning, afternoon and night kickoffs, using 263 games from the 2007–2025 seasons. A Mann-Whitney U test compares home and away margins. ANCOVA (multiple regression with control variables) then compares kickoff times and home field while holding opponent strength constant. Without that control, morning games look much better, but only because they are scheduled against weaker opponents.

## Method

1. **Mann-Whitney U test (home vs away).** A rank-based test, so it doesn't require normally distributed data. Computed by hand in Excel: ranks with `RANK.AVG`, U statistics, a tie-corrected standard deviation, then a normal-approximation z and p-value.
2. **ANCOVA / multiple regression.** Point margin regressed on game site and kickoff time, controlling for opponent strength (ranked or not) and conference play (SEC or non-conference). Reference groups: **away** for site and **afternoon** for kickoff time. Run with Excel's Analysis ToolPak.
3. **Assumption testing.** `regression_assumptions.py` checks the regression assumptions: additivity (an interaction term), independence (Durbin-Watson), equal variance (Breusch-Pagan), normal residuals (Shapiro-Wilk and a Q-Q plot), multicollinearity (VIF) and influential games (Cook's distance).

Kickoff times are Central time: morning is before 12:00 p.m., afternoon is 12:00–4:59 p.m., and night is 5:00 p.m. or later.

## Data

`alabama_games_2007_2025.csv` has one row per game: 263 games, including regular season, SEC Championship, bowl and College Football Playoff games. It was compiled from the public Wikipedia season pages ("20XX Alabama Crimson Tide football team"), which are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Season records were checked against Alabama's official records.

| Column | Description |
|---|---|
| `season`, `date` | Season year and game date |
| `time_raw`, `kickoff_ct` | Kickoff time as listed, and as a decimal hour in Central time |
| `opponent`, `opp_ranked`, `opp_rank` | Opponent, whether it was ranked (AP/CFP), and its rank |
| `non_conf` | 1 = non-conference game |
| `site` | home / away / neutral |
| `result`, `pts_for`, `pts_against`, `margin` | Result and score; margin = Alabama points minus opponent points |

## Files

| File | Contents |
|---|---|
| `Alabama_Football_Performance_Using_Mann_Whitney_and_ANCOVA.xlsm` | Data, Mann-Whitney U calculations, ANCOVA regression output, and assumption testing |
| `alabama_games_2007_2025.csv` | Game-level dataset |
| `regression_assumptions.py` | Python checks of the regression assumptions, with diagnostic plots |

## How to run

**Excel:** open the workbook. Re-running the regression requires the Analysis ToolPak (File → Options → Add-ins → Excel Add-ins → Analysis ToolPak).

**Python** (3.10+):

```bash
pip install -r requirements.txt
python regression_assumptions.py
```

The script prints each assumption check and saves a plot to `figures/regression_assumptions.png`.

## Key results

**Home vs away (Mann-Whitney U):** Alabama's margins were significantly higher at home (U = 7,484, z = 4.46, p < 0.0001). In 68% of home–away matchups, the home game had the larger margin.

**ANCOVA (controlling for opponent strength, conference and site):**

| Factor | Effect on point margin | p-value |
|---|---|---|
| Ranked opponent (vs unranked) | −11.3 | < 0.001 |
| Non-conference (vs SEC) | +9.2 | < 0.001 |
| Home (vs away) | +8.0 | 0.001 |
| Neutral site (vs away) | −4.6 | 0.21 |
| Morning (vs afternoon) | +3.4 | 0.32 |
| Night (vs afternoon) | +0.9 | 0.67 |

R² = 0.289. Baseline (intercept): Alabama is predicted to win an away afternoon game against an unranked SEC opponent by 19.1 points.

- **Kickoff time has no significant effect.** Before adjustment, morning games averaged +31.1 versus +18.5 in the afternoon (ANOVA p = 0.004). After controlling for opponent strength, the difference disappears (ANCOVA F(2, 256) = 0.51, p = 0.60). Only 9% of morning opponents were ranked, compared with about half in the afternoon and at night.
- **Home field is worth about 8 points.** That's smaller than the raw 12-point gap, because Alabama's home schedule includes more weak non-conference opponents.
- **Assumptions were met.** Durbin-Watson = 1.79 (weak, non-significant autocorrelation that doesn't affect the results), Breusch-Pagan p = 0.12, Shapiro-Wilk p = 0.58, all VIFs < 2, maximum Cook's distance = 0.038.

**Conclusion:** Alabama's performance depends on *who* it plays and *where*, not *when*.

## Limitations

- Opponent strength is measured only as ranked or unranked. A finer measure, such as the point spread or SP+, would control for it more precisely.
- The data is observational: kickoff times are chosen by TV networks, not assigned at random.
- The results apply to Alabama from 2007 to 2025 and may not generalize to other teams.
