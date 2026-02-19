import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter


# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


# Load the cleaned data
matches = pd.read_csv('matches_cleaned.csv')
deliveries = pd.read_csv('deliveries_cleaned.csv')


print("\n" + "="*80)
print("IPL DATA EXPLORATION - COMPREHENSIVE EDA")
print("="*80)


# ==================== 1. TOP BATSMEN ANALYSIS ====================
print("\n" + "-"*80)
print("1. TOP BATSMEN ANALYSIS")
print("-"*80)


# Calculate runs, strike rate, 4s, and 6s for each batter
batsmen_stats = deliveries.groupby('batter').agg({
    'batsman_runs': 'sum',  # Total runs
    'ball': 'count',         # Balls faced (used for strike rate)
}).rename(columns={'batsman_runs': 'runs', 'ball': 'balls_faced'})


# Count 4s and 6s
fours = deliveries[deliveries['batsman_runs'] == 4].groupby('batter').size()
sixes = deliveries[deliveries['batsman_runs'] == 6].groupby('batter').size()


batsmen_stats['fours'] = fours
batsmen_stats['sixes'] = sixes
batsmen_stats = batsmen_stats.fillna(0).astype({'fours': int, 'sixes': int})


# Calculate strike rate (runs / balls_faced * 100)
batsmen_stats['strike_rate'] = (batsmen_stats['runs'] / batsmen_stats['balls_faced'] * 100).round(2)


# Filter players with minimum 50 balls faced for credibility
batsmen_stats_filtered = batsmen_stats[batsmen_stats['balls_faced'] >= 50].sort_values('runs', ascending=False)


print("\nTop 20 Batsmen by Runs:")
print(batsmen_stats_filtered[['runs', 'balls_faced', 'strike_rate', 'fours', 'sixes']].head(20))


# Visualization: Top 15 batsmen by runs
fig, axes = plt.subplots(2, 2, figsize=(16, 12))


# Plot 1: Top 15 Batsmen by Runs
top_batsmen = batsmen_stats_filtered.head(15)
axes[0, 0].barh(range(len(top_batsmen)), top_batsmen['runs'], color='steelblue')
axes[0, 0].set_yticks(range(len(top_batsmen)))
axes[0, 0].set_yticklabels(top_batsmen.index)
axes[0, 0].set_xlabel('Runs', fontsize=12)
axes[0, 0].set_title('Top 15 Batsmen by Runs', fontsize=14, fontweight='bold')
axes[0, 0].invert_yaxis()


# Plot 2: Strike Rate vs Runs (Minimum 50 balls)
axes[0, 1].scatter(batsmen_stats_filtered['runs'], batsmen_stats_filtered['strike_rate'],
                   s=batsmen_stats_filtered['balls_faced']/2, alpha=0.6, c=batsmen_stats_filtered['runs'], cmap='viridis')
axes[0, 1].set_xlabel('Total Runs', fontsize=12)
axes[0, 1].set_ylabel('Strike Rate', fontsize=12)
axes[0, 1].set_title('Strike Rate vs Runs (Bubble size = Balls Faced)', fontsize=14, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3)


# Plot 3: Top 10 Batsmen - Fours and Sixes
top10_batsmen = batsmen_stats_filtered.head(10)
x = np.arange(len(top10_batsmen))
width = 0.35
axes[1, 0].bar(x - width/2, top10_batsmen['fours'], width, label='Fours', color='orange')
axes[1, 0].bar(x + width/2, top10_batsmen['sixes'], width, label='Sixes', color='red')
axes[1, 0].set_xlabel('Batsmen', fontsize=12)
axes[1, 0].set_ylabel('Count', fontsize=12)
axes[1, 0].set_title('Top 10 Batsmen - Fours and Sixes', fontsize=14, fontweight='bold')
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(top10_batsmen.index, rotation=45, ha='right')
axes[1, 0].legend()


# Plot 4: Top 15 by Strike Rate
top_sr = batsmen_stats_filtered.nlargest(15, 'strike_rate')
axes[1, 1].barh(range(len(top_sr)), top_sr['strike_rate'], color='seagreen')
axes[1, 1].set_yticks(range(len(top_sr)))
axes[1, 1].set_yticklabels(top_sr.index)
axes[1, 1].set_xlabel('Strike Rate', fontsize=12)
axes[1, 1].set_title('Top 15 Batsmen by Strike Rate', fontsize=14, fontweight='bold')
axes[1, 1].invert_yaxis()


plt.tight_layout()
plt.savefig('top_batsmen_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: top_batsmen_analysis.png")
plt.close()


# ==================== 2. TOP BOWLERS ANALYSIS ====================
print("\n" + "-"*80)
print("2. TOP BOWLERS ANALYSIS")
print("-"*80)


# Calculate bowlers statistics
bowlers_stats = pd.DataFrame()


# Total wickets taken (count of player_dismissed by bowler)
wickets = deliveries[deliveries['is_wicket'] == 1].groupby('bowler').size()
bowlers_stats['wickets'] = wickets


# Total balls bowled (count of deliveries)
balls_bowled = deliveries.groupby('bowler').size()
bowlers_stats['balls_bowled'] = balls_bowled


# Total runs conceded
runs_conceded = deliveries.groupby('bowler')['total_runs'].sum()
bowlers_stats['runs_conceded'] = runs_conceded


# Calculate economy rate (runs conceded per over)
bowlers_stats['overs'] = (bowlers_stats['balls_bowled'] / 6).round(2)
bowlers_stats['economy_rate'] = (bowlers_stats['runs_conceded'] / (bowlers_stats['balls_bowled'] / 6)).round(2)


# Dot ball percentage
dot_balls = deliveries[deliveries['bowler'].notna() & (deliveries['total_runs'] == 0)].groupby('bowler').size()
bowlers_stats['dot_balls'] = dot_balls
bowlers_stats['dot_ball_percentage'] = ((bowlers_stats['dot_balls'] / bowlers_stats['balls_bowled']) * 100).round(2)


# Fill NaN values with 0 for dot balls
bowlers_stats = bowlers_stats.fillna(0).astype({'wickets': int, 'dot_balls': int})


# Filter bowlers with minimum 50 balls bowled for credibility
bowlers_stats_filtered = bowlers_stats[bowlers_stats['balls_bowled'] >= 50].sort_values('wickets', ascending=False)


print("\nTop 20 Bowlers by Wickets:")
print(bowlers_stats_filtered[['wickets', 'economy_rate', 'dot_ball_percentage', 'balls_bowled']].head(20))


# Visualization: Bowlers Analysis
fig, axes = plt.subplots(2, 2, figsize=(16, 12))


# Plot 1: Top 15 Bowlers by Wickets
top_bowlers = bowlers_stats_filtered.head(15)
axes[0, 0].barh(range(len(top_bowlers)), top_bowlers['wickets'], color='crimson')
axes[0, 0].set_yticks(range(len(top_bowlers)))
axes[0, 0].set_yticklabels(top_bowlers.index)
axes[0, 0].set_xlabel('Wickets', fontsize=12)
axes[0, 0].set_title('Top 15 Bowlers by Wickets', fontsize=14, fontweight='bold')
axes[0, 0].invert_yaxis()


# Plot 2: Economy Rate vs Wickets
axes[0, 1].scatter(bowlers_stats_filtered['economy_rate'], bowlers_stats_filtered['wickets'],
                   s=bowlers_stats_filtered['balls_bowled']/2, alpha=0.6, c=bowlers_stats_filtered['wickets'], cmap='cool')
axes[0, 1].set_xlabel('Economy Rate', fontsize=12)
axes[0, 1].set_ylabel('Wickets', fontsize=12)
axes[0, 1].set_title('Economy Rate vs Wickets (Bubble size = Balls Bowled)', fontsize=14, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3)


# Plot 3: Top 15 Bowlers by Dot Ball Percentage
top_dot = bowlers_stats_filtered.nlargest(15, 'dot_ball_percentage')
axes[1, 0].barh(range(len(top_dot)), top_dot['dot_ball_percentage'], color='navy')
axes[1, 0].set_yticks(range(len(top_dot)))
axes[1, 0].set_yticklabels(top_dot.index)
axes[1, 0].set_xlabel('Dot Ball Percentage (%)', fontsize=12)
axes[1, 0].set_title('Top 15 Bowlers by Dot Ball Percentage', fontsize=14, fontweight='bold')
axes[1, 0].invert_yaxis()


# Plot 4: Top 10 Bowlers - Economy Rate
top10_eco = bowlers_stats_filtered.nsmallest(10, 'economy_rate')
axes[1, 1].barh(range(len(top10_eco)), top10_eco['economy_rate'], color='darkgreen')
axes[1, 1].set_yticks(range(len(top10_eco)))
axes[1, 1].set_yticklabels(top10_eco.index)
axes[1, 1].set_xlabel('Economy Rate', fontsize=12)
axes[1, 1].set_title('Best 10 Bowlers by Economy Rate', fontsize=14, fontweight='bold')
axes[1, 1].invert_yaxis()


plt.tight_layout()
plt.savefig('top_bowlers_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: top_bowlers_analysis.png")
plt.close()


# ==================== 3. TEAM RIVALRIES ANALYSIS ====================
print("\n" + "-"*80)
print("3. TEAM RIVALRIES ANALYSIS")
print("-"*80)


# Head-to-head records between teams
h2h_records = {}


for idx, row in matches.iterrows():
    team1 = row['team1']
    team2 = row['team2']
    winner = row['winner']
   
    # Create a key that's always in the same order
    teams = tuple(sorted([team1, team2]))
   
    if teams not in h2h_records:
        h2h_records[teams] = {'total': 0, team1: 0, team2: 0}
   
    h2h_records[teams]['total'] += 1
   
    if pd.notna(winner):
        if winner == team1 or winner == team2:
            h2h_records[teams][winner] += 1


# Convert to DataFrame for easier viewing
h2h_list = []
for teams, record in h2h_records.items():
    h2h_list.append({
        'Team1': teams[0],
        'Team2': teams[1],
        f'{teams[0]}_Wins': record[teams[0]],
        f'{teams[1]}_Wins': record[teams[1]],
        'Total_Matches': record['total']
    })


h2h_df = pd.DataFrame(h2h_list).sort_values('Total_Matches', ascending=False)


print("\nTop 20 Team Rivalries (Most Matches):")
print(h2h_df.head(20))


# Most wins by team
team_wins = matches[matches['winner'].notna()].groupby('winner').size().sort_values(ascending=False)
print("\n\nMost Wins by Team:")
print(team_wins.head(15))


# Visualization: Team Rivalries
fig, axes = plt.subplots(2, 1, figsize=(16, 12))


# Plot 1: Top 12 Rivalries (by number of matches)
top_rivalries = h2h_df.head(12)
rivalry_labels = [f"{row['Team1']} vs {row['Team2']}" for _, row in top_rivalries.iterrows()]
x = np.arange(len(top_rivalries))
width = 0.35


axes[0].bar(x - width/2, top_rivalries[top_rivalries.columns[2]], width, label=top_rivalries['Team1'], color='skyblue')
axes[0].bar(x + width/2, top_rivalries[top_rivalries.columns[3]], width, label=top_rivalries['Team2'], color='lightcoral')
axes[0].set_xlabel('Teams', fontsize=12)
axes[0].set_ylabel('Wins', fontsize=12)
axes[0].set_title('Top 12 Rivalries - Head to Head Records', fontsize=14, fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels(rivalry_labels, rotation=45, ha='right', fontsize=9)
axes[0].legend()
axes[0].grid(True, axis='y', alpha=0.3)


# Plot 2: Most Wins by Team
top_teams = team_wins.head(15)
axes[1].barh(range(len(top_teams)), top_teams.values, color='gold')
axes[1].set_yticks(range(len(top_teams)))
axes[1].set_yticklabels(top_teams.index)
axes[1].set_xlabel('Number of Wins', fontsize=12)
axes[1].set_title('Most Wins by Team (Overall)', fontsize=14, fontweight='bold')
axes[1].invert_yaxis()


plt.tight_layout()
plt.savefig('team_rivalries_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: team_rivalries_analysis.png")
plt.close()


# ==================== 4. WINNING FACTORS ANALYSIS ====================
print("\n" + "-"*80)
print("4. WINNING FACTORS ANALYSIS")
print("-"*80)


# Toss winner effect on match outcome
toss_analysis = matches[matches['winner'].notna()].copy()
toss_analysis['toss_won'] = toss_analysis['toss_winner'] == toss_analysis['winner']


toss_wins = toss_analysis['toss_won'].value_counts()
toss_win_percentage = (toss_analysis['toss_won'].sum() / len(toss_analysis) * 100)


print(f"\nToss Winner Impact:")
print(f"Matches where toss winner also won: {toss_wins.get(True, 0)}")
print(f"Matches where toss winner lost: {toss_wins.get(False, 0)}")
print(f"Toss Winner Success Rate: {toss_win_percentage:.2f}%")


# Toss decision impact
print("\n\nToss Decision Impact (Win %:")
toss_decision_analysis = toss_analysis.copy()
toss_decision_analysis['decision_correct'] = toss_decision_analysis['toss_winner'] == toss_decision_analysis['winner']
decision_impact = toss_decision_analysis.groupby('toss_decision').apply(
    lambda x: (x['decision_correct'].sum() / len(x) * 100) if len(x) > 0 else 0
)
print(decision_impact)


# Venue impact
print("\n\nTop 10 Venues by Match Count:")
venue_matches = matches['venue'].value_counts().head(10)
print(venue_matches)


venue_winners = matches[matches['winner'].notna()].groupby('venue')['winner'].value_counts().unstack(fill_value=0)


# Season analysis
print("\n\nMatches by Season:")
season_matches = matches['season'].value_counts().sort_index()
print(season_matches)


print("\nWins by Season:")
season_wins = matches[matches['winner'].notna()].groupby('season')['winner'].value_counts()
print(season_wins.head(20))


# Visualization: Winning Factors
fig, axes = plt.subplots(2, 2, figsize=(16, 12))


# Plot 1: Toss Winner Success Rate
toss_data = pd.Series([toss_wins.get(True, 0), toss_wins.get(False, 0)],
                       index=['Toss Winner Won', 'Toss Winner Lost'])
colors = ['#2ecc71', '#e74c3c']
axes[0, 0].pie(toss_data.values, labels=toss_data.index, autopct='%1.1f%%', startangle=90, colors=colors)
axes[0, 0].set_title('Toss Winner Match Outcome Impact', fontsize=14, fontweight='bold')


# Plot 2: Toss Decision Impact
decision_impact_df = pd.DataFrame({
    'Decision': decision_impact.index,
    'Win_Percentage': decision_impact.values
})
axes[0, 1].bar(decision_impact_df['Decision'], decision_impact_df['Win_Percentage'], color=['#3498db', '#e67e22'])
axes[0, 1].set_ylabel('Win Percentage (%)', fontsize=12)
axes[0, 1].set_xlabel('Toss Decision', fontsize=12)
axes[0, 1].set_title('Toss Decision Impact on Match Outcome', fontsize=14, fontweight='bold')
axes[0, 1].set_ylim([0, 100])
for i, v in enumerate(decision_impact_df['Win_Percentage']):
    axes[0, 1].text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')


# Plot 3: Top 12 Venues by Match Count
top_venues = matches['venue'].value_counts().head(12)
axes[1, 0].barh(range(len(top_venues)), top_venues.values, color='mediumpurple')
axes[1, 0].set_yticks(range(len(top_venues)))
axes[1, 0].set_yticklabels(top_venues.index, fontsize=10)
axes[1, 0].set_xlabel('Number of Matches', fontsize=12)
axes[1, 0].set_title('Top 12 Venues by Match Count', fontsize=14, fontweight='bold')
axes[1, 0].invert_yaxis()


# Plot 4: Matches by Season
season_data = matches['season'].value_counts().sort_index()
axes[1, 1].plot(season_data.index.astype(str), season_data.values, marker='o', linewidth=2, markersize=8, color='darkblue')
axes[1, 1].fill_between(range(len(season_data)), season_data.values, alpha=0.3, color='lightblue')
axes[1, 1].set_xlabel('Season', fontsize=12)
axes[1, 1].set_ylabel('Number of Matches', fontsize=12)
axes[1, 1].set_title('Matches Played by Season', fontsize=14, fontweight='bold')
axes[1, 1].grid(True, alpha=0.3)
plt.setp(axes[1, 1].xaxis.get_majorticklabels(), rotation=45, ha='right')


plt.tight_layout()
plt.savefig('winning_factors_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: winning_factors_analysis.png")
plt.close()


print("\n" + "="*80)
print("EDA COMPLETE - All visualizations saved!")
print("="*80)



