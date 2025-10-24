import { buildLineupSuggestions, formatPoints } from "@/lib/roster-utils";
import { LeagueRosterResponse } from "@/lib/api-types";

describe("roster utils", () => {
  const roster: LeagueRosterResponse = {
    league_key: "nfl.l.1",
    week: 5,
    team: { team_key: "team1", name: "Phoenix Firebirds", manager: "Taylor" },
    generated_at: new Date().toISOString(),
    starters: [
      {
        slot: "QB",
        player: {
          yahoo_player_id: "1",
          full_name: "Josh Allen",
          team_abbr: "BUF",
          position: "QB",
          projected_points: 25.5,
          actual_points: 24.1,
          status: "ACTIVE"
        },
        recommended: true,
        locked: false
      },
      {
        slot: "RB1",
        player: {
          yahoo_player_id: "2",
          full_name: "James Conner",
          team_abbr: "ARI",
          position: "RB",
          projected_points: 12.0,
          actual_points: 8.4,
          status: "QUESTIONABLE"
        },
        recommended: false,
        locked: false
      }
    ],
    bench: [
      {
        slot: "RB1",
        player: {
          yahoo_player_id: "3",
          full_name: "Jahmyr Gibbs",
          team_abbr: "DET",
          position: "RB",
          projected_points: 17.6,
          actual_points: null,
          status: "ACTIVE"
        },
        recommended: false,
        locked: false
      },
      {
        slot: "BENCH",
        player: {
          yahoo_player_id: "4",
          full_name: "Courtland Sutton",
          team_abbr: "DEN",
          position: "WR",
          projected_points: 9.1,
          actual_points: null,
          status: "ACTIVE"
        },
        recommended: false,
        locked: false
      }
    ],
    optimizer: {
      recommended_starters: ["Josh Allen", "Jahmyr Gibbs"],
      delta_points: 5.6,
      rationale: ["Start Jahmyr Gibbs over James Conner for +5.6 points."],
      source: "optimizer"
    }
  };

  it("builds suggestions pairing bench upgrades to starter slots", () => {
    const suggestions = buildLineupSuggestions(roster);
    expect(suggestions).toHaveLength(1);
    expect(suggestions[0].from.player.full_name).toBe("James Conner");
    expect(suggestions[0].to.player.full_name).toBe("Jahmyr Gibbs");
    expect(suggestions[0].delta).toBeCloseTo(5.6, 1);
  });

  it("formats point totals with one decimal place", () => {
    expect(formatPoints(10)).toBe("10.0");
    expect(formatPoints(null)).toBe("-");
  });
});
