# PyESPN Index and Glossary

This document provides a comprehensive index and glossary of the PyESPN package.
PyESPN is a Python client library that interacts with ESPN’s public sports data APIs, allowing developers to
fetch game schedules, player statistics, betting odds, recruiting rankings, and more.
The index lists all major classes, objects, exceptions, attributes, methods, and properties documented in the
official PyESPN documentation and source code.
Each entry includes a brief description and cites the official documentation lines or source code where the
element is defined or explained. 

## How to use this document

- **Index:** Browse the alphabetical index to locate a class, method, or attribute.  
- **Glossary:** Refer to the glossary section for definitions of specific terms used in PyESPN (e.g., betting‑related terminology).

> **Note:** This index only includes elements confirmed from the official PyESPN documentation
> or source code. No assumptions or inferred members are listed.
> Each citation links back to the original documentation lines where the description or
> definition appears. 

---

## Index

### A–C

| Element | Description and callable details | Official sources |
|---|---|---|
| **API400Error** | Custom exception raised when ESPN’s API returns a 400 Bad Request error. It accepts an `error_code` and an `error_message` and formats them into the exception message. | Exceptions module |
| **Alternate IDs (Player)** | Attribute of a player containing a dictionary of other identifier types (e.g., `sdr`, `espn`) loaded from the API response. | Player class |
| **Athletes (LeaderCategory)** | A dictionary keyed by season; each value is a list of `Leader` objects representing statistical leaders for that season. | LeaderCategory class |
| **API version** | Not a callable element; stored in the `Client` class as the `v` attribute denoting the ESPN API version. | Client class |
| **Away team (Event)** | Property returning the away team in a particular event. This property loads the team from the event JSON when accessed. | Event class |
| **Betting** | Class encapsulating betting data for an event. It stores raw `betting_json`, the `espn_instance`, and a list of `Provider` objects. Methods: `_set_betting_data()` (internal), `to_dict()` to convert to JSON, and `__repr__()` for a string representation. | Betting class |
| **Betting Futures (League)** | Property in `League` that holds futures bets available for the league. It is populated by `get_all_seasons_futures()`. | League class |
| **Bet Value** | Represents an individual betting value within a betting category. Attributes: `name`, `bet_json`, `espn_instance`. Methods: `to_dict()` to return the raw JSON and `__repr__()` for representation. | BetValue class |
| **Birth city/state (Player)** | Attributes giving a player’s place of birth (`birth_city`, `birth_state`). | Player class |
| **Box scores** | Functionality to load player box scores for a season is provided by `load_player_box_scores_season(season)` in the `Player` class. | Player class |
| **Chassis (Vehicle)** | Attribute in the `Vehicle` class describing a racing vehicle’s chassis. | Vehicle class |
| **Citizenship (Player)** | Attribute giving player’s citizenship information. | Player class |
| **Client** | Main entry point class for the PyESPN API. Constructor accepts `sport_league` (abbreviation like `nfl`, `nba`) and `load_teams` (bool). Attributes: `league_abbv`, `teams`, `league`, `team_id_mapping`, `betting_providers`, `league_division_betting_keys`, `api_mapping`, `standings`, `drafts`, `recruit_rankings`, `athletes`, `manufacturers`, and `v` for API version. Methods include `get_awards(season)`, `get_draft_pick_data(season, pick_round, pick)`, `get_game_info(event_id)`, `get_player_ids(season)`, `get_player_info(player_id)`, `get_players_historical_stats(player_id)`, `get_recruiting_rankings(season, max_pages=None)`, `get_season_team_stats(season)`, `get_team_by_id(team_id)`, `load_athletes(season)`, `load_season_coaches(season)`, `load_season_league_stat_leaders(season)`, `load_season_rosters(season)`, `load_season_team_stats(season)`, `load_season_teams_results(season)`, `load_seasons_betting_records(season)`, `load_seasons_futures(season)`, `load_standings(season)`, `load_year_draft(season)`, and `load_year_recruiting_rankings(year)`. | Client class and method citations |
| **Clock (Play)** | Attribute representing the game clock at the time of the play. It is part of the `Play` object loaded from the event’s play‑by‑play JSON. | Play class |
| **Competition** | Lightweight class representing a competition. Provides `id` property, `espn_instance` property, `to_dict()` to return raw JSON, and `__repr__()` for human‑readable representation. | Competition class |
| **Contracts (Player)** | Method `load_player_contracts()` loads contract details for a player; the `contracts_ref` attribute stores the API URL for contract data. | Player class |

### D–F

| Element | Description and callable details | Official sources |
|---|---|---|
| **Date (Event)** | Attribute giving the date and time of the event; loaded from the event JSON. | Event class |
| **Display name (Team/Player/League)** | Human‑friendly name for the object. `Team.display_name`, `Player.display_name`, and `League.display_name` provide this value. | Team, Player, League classes |
| **Draft** | Represented by the `DraftPick` class (see DraftPick). The `Client` provides `load_year_draft(season)` to load a league’s draft for a given year. | Client and DraftPick classes |
| **DraftPick** | Class representing a single draft pick. Attributes: `pick_json` (raw JSON), `espn_instance`, `athlete` (`Player`), `team` (`Team`), `round_number`, `pick_number`, and `overall_number`. Methods: `_get_pick_data()` loads these attributes, `to_dict()` returns raw JSON, and `__repr__()` provides a formatted string. | DraftPick class |
| **Drive** | Represents a single drive in a game’s play‑by‑play. Attributes: `drive_json`, `espn_instance`, `event_instance`, `description`, `id`, `sequence_number`, `ref`, `start`, `end`, `time_elapsed`, `yards`, `is_score`, `offensive_plays`, `result`, `result_display`, `team`, `end_team`, `plays_ref`, and `plays`. Methods: `_load_drive_data()` (loads attributes), `_load_plays()` (builds `Play` objects), `to_dict()` (returns raw JSON), `__repr__()`. | Drive class |
| **Engine (Vehicle)** | Attribute describing the engine manufacturer or specification for a racing vehicle. | Vehicle class |
| **Event** | Core object representing a single sporting event. Attributes include `event_json`, `espn_instance`, `url_ref`, `event_id`, `date`, `event_name`, `short_name`, `competition_type`, `venue_json`, `event_venue` (a `Venue`), `event_notes`, `home_team`, `away_team`, `api_info`, `competition` (`Competition`), `odds`, `drives`, `plays`, and more. Methods: `__init__(event_json, espn_instance, load_game_odds=False, load_play_by_play=False)` loads the event; `load_betting_odds()` fetches odds using multithreading; `load_play_by_play()` loads drives and plays; `to_dict()` returns raw JSON; `__repr__()` returns a formatted string. | Event class |
| **Experience/Years (Player)** | Attributes describing the player’s professional experience and years in the league. | Player class |
| **Experience (Recruit)** | Attribute representing the recruiting class year (`recruiting_class`) and grade of a recruit. | Recruit class |

### G–L

| Element | Description and callable details | Official sources |
|---|---|---|
| **Game Odds** | Class modelling overall betting odds for an event. Attributes include `provider`, `over_under`, `details`, `spread`, `over_odds`, `under_odds`, `money_line_winner`, `spread_winner`, `open`, `current`, `close`, and nested `home_team_odds` / `away_team_odds` (as `Odds` or `OddsBet365`). Methods: `_load_odds_data()` processes provider‑specific logic, `to_dict()` returns raw JSON, and `__repr__()`. | GameOdds class |
| **Guid (Team/Player/Recruit)** | Unique global identifier for teams, players, or recruits. Stored as `guid` and loaded from the API response. | Team, Player, Recruit classes |
| **Height/Weight** | Attributes for players and recruits describing physical measurements. `height`, `display_height`, `weight`, and `display_weight` are loaded during object creation. | Player, Recruit classes |
| **Home team (Event)** | Property returning the home team from the event JSON. | Event class |
| **Image** | Class representing an image object retrieved from the ESPN API. Attributes include `ref` (URL), `name`, `width`, `height`, `alt`, `rel`, `last_updated`, and the raw `image_json`. Methods: `load_image()` returns the binary content of the image, `to_dict()` returns raw JSON, and `__repr__()` provides a string representation. | Image class |
| **InvalidLeagueError** | Exception raised when a league abbreviation passed to the `Client` is not valid. It takes `league_abbv` and returns a descriptive error message. | Exceptions module |
| **Is active (Team)** | Attribute indicating whether the team is currently active. Loaded from the team JSON. | Team class |
| **League** | Class representing a sports league. It stores metadata such as `ref`, `id`, `name`, `display_name`, `abbreviation`, `short_name`, `slug`, `is_tournament`, `season`, `seasons`, `franchises`, `teams`, `group`, `groups`, `events`, `notes`, `rankings`, `draft`, and `links`. Properties: `league_leaders`, `schedules`, and `betting_futures`. Methods: `load_regular_season_schedule(season, load_game_odds=False, load_game_play_by_play=False)` loads schedule; `get_event_by_season(season, event_id)` retrieves an event; `get_all_seasons_futures(season)` fetches betting futures concurrently; `fetch_leader_category(category, season)` returns a `LeaderCategory`; `load_season_league_leaders(season)` fetches and caches league leaders; `to_dict()` returns raw JSON. | League class |
| **Leader** | Represents a statistical leader in a category for a season. Attributes: `rank`, `athlete` (`Player`), `team` (`Team`), `value`, `rel`, etc. Methods: `to_dict()` returns raw JSON, `__repr__()` returns a string representation. Constructed via the `LeaderCategory` class. | Leader class |
| **LeaderCategory** | Represents a category of statistical leaders. Attributes: `abbreviation`, `name`, `display_name`, and a dictionary `athletes` keyed by season containing lists of `Leader` objects. Methods: `_load_leaders_data()` (internal), `to_dict()` returns raw JSON, and `__repr__()`. | LeaderCategory class |
| **LeagueNotAvailableError** | Exception raised when the ESPN API supports a league but it is not currently available in PyESPN. | Exceptions module |
| **LeagueNotSupportedError** | Exception raised when a requested league is not supported by PyESPN. It accepts a `league_abbv` and produces a descriptive message. | Exceptions module |
| **Length (Circuit)** | Attribute describing the total length of a racing circuit. Part of the `Circuit` object. | Circuit class |
| **Line** | Class representing an individual betting line. Attributes: `espn_instance`, `provider_instance`, `book_json`, `athlete` (`Player` or `None`), `team` (`Team` or `None`), `ref`, and `value`. Methods: `_set_line_data()` reads JSON to create `Player` or `Team` objects from references, `to_dict()` returns raw JSON, and `__repr__()` provides a human‑readable representation. | Line class |
| **Load season league stat leaders** | Method of `Client` that loads statistical leaders for a season; it populates the league’s `league_leaders` property. | Client class |
| **Load season team stats** | Method of `Client` that loads statistical data for each team in the league for a given season. | Client class |
| **Load season teams results** | Method of `Client` that loads win/loss and game results for each team in a season. | Client class |
| **Load seasons betting records** | Method of `Client` that loads betting record information for a given season. | Client class |
| **Load seasons futures** | Method of `Client` that loads betting futures for a particular season. | Client class |
| **Load standings** | Method of `Client` that fetches standings for a specified season and populates the `standings` attribute. | Client class |
| **Load year draft** | Method of `Client` that loads the draft for a particular year. | Client class |
| **Load year recruiting rankings** | Method of `Client` that loads recruiting rankings for a given year and stores them in the `recruit_rankings` attribute. | Client class |

### M–R

| Element | Description and callable details | Official sources |
|---|---|---|
| **Manufacturer** | Class representing a racing manufacturer. Attributes: `api_ref`, `id`, `name`, `display_name`, `short_display_name`, `abbreviation`, `color`, `event_log_ref`. Methods: `to_dict()` returns raw JSON and `__repr__()` provides a formatted string. | Manufacturer class |
| **Money line (Odds/OddsBet365)** | Attribute representing the money‑line betting odds for a team. In `Odds` it is part of the nested `OddsType` objects for `open`, `current`, and `close`; in `OddsBet365` it is parsed directly for Bet365 providers. | Odds and OddsBet365 classes |
| **Name (Team/Player/League)** | Core identifying attribute (e.g., team name). `Team.name`, `Player.first_name` / `last_name`, `League.name` provide these values. | Team, Player, League classes |
| **NoDataReturnedError** | Exception raised when a request to the ESPN API returns no data; used to indicate missing results. | Exceptions module |
| **Odds** | Represents betting odds for a team. Attributes: `favorite`, `underdog`, `money_line`, `spread_odds`, `team`, and `open`, `current`, `close` which are `OddsType` objects. Methods: `_load_odds_json()` populates these attributes, `to_dict()` returns raw JSON, and `__repr__()` returns a string showing the team name. | Odds class |
| **OddsBet365** | Subclass of `Odds` designed to handle Bet365’s JSON format. In addition to `money_line` and `spread_odds`, it also stores `teaser_odds`. Methods: `_load_odds_json()` processes Bet365‑specific fields, `to_dict()` returns raw JSON, and `__repr__()` returns `<Odds365 | team.name>`. | OddsBet365 class |
| **OddsType** | Represents a specific category of betting odds (e.g., open, current, or close). Attributes include `name`, `favorite`, `odds` (mapping of bet types to `BetValue`), etc. Methods: `to_dict()` returns raw JSON and `__repr__()` provides a string representation. | OddsType class |
| **Overall number (DraftPick)** | Attribute giving the overall pick number in a draft. | DraftPick class |
| **Participants (Play)** | List of participant objects (players involved in a play) included in the `participants` attribute of a `Play` object. | Play class |
| **Per game value (Stat)** | Value of a statistic on a per‑game basis. Part of the `Stat` object. | Stat class |
| **Period (Play)** | Attribute indicating the period/quarter when the play occurred. | Play class |
| **Play** | Class representing a single play in a play‑by‑play. Attributes: `play_json`, `espn_instance`, `event_instance`, `drive_instance`, `team`, `id`, `text`, `short_text`, `alt_text`, `short_alt_text`, `home_score`, `away_score`, `sequence_number`, `type`, `period`, `clock`, `scoring_play`, `priority`, `score_value`, `start`, `end`, `wallclock`, `modified`, `probability`, `stat_yardage`, `participants`, `shooting_play`, `coordinate`, etc. Methods: `_load_play_data()` parses the JSON, `to_dict()` returns raw JSON, and `__repr__()` returns a formatted string. | Play class |
| **Player** | Extensive class representing an athlete. Attributes include identity fields (`api_ref`, `id`, `uid`, `guid`, `type`), demographics (`flag`, `citizenship`, `experience`, `experience_years`, `first_name`, `last_name`, `full_name`, `display_name`, `short_name`, `weight`, `display_weight`, `height`, `display_height`, `age`, `date_of_birth`), career fields (`debut_year`, `college_athlete_ref`, `links`), position information (`position_ref`, `position_id`, `position_name`, `position_display_name`, `position_abbreviation`, `position_leaf`, `position_parent_ref`), team and status fields (`team_ref`, `active`, `status_id`, `status_name`, `status_type`, `status_abbreviation`), vehicles (list of `Vehicle` objects), and more. Methods include `load_player_historical_stats()`, `load_player_box_scores_season(season)`, `load_player_contracts()`, and `to_dict()`. | Player class |
| **Position (Player/Recruit)** | Attributes describing a player’s or recruit’s position: `position_id`, `position_name`, `position_display_name`, `position_abbreviation`, `position_leaf`, `position_parent_ref`. | Player and Recruit classes |
| **Probabilities (Play)** | Attribute providing win‑probability information at the time of the play. | Play class |
| **Provider (GameOdds)** | The betting provider (e.g., “consensus” or “Bet365”). Stored in the `provider` attribute of `GameOdds`. | GameOdds class |
| **Record** | Class representing a standings record. Attributes: `stats` (list of `Stat` objects), `id`, `ref`, `name`, `abbreviation`, `display_name`, `short_display_name`, `description`, and `type`. Methods: `_load_record_data()` populates the object, `to_dict()` returns raw JSON, and `__repr__()` produces a readable string. | Record class |
| **Recruit** | Represents a high‑school recruit. Attributes include `api_ref`, `athlete`, `id`, `uid`, `guid`, `type`, `alternate_ids`, `first_name`, `last_name`, `full_name`, `display_name`, `short_name`, `weight`, `height`, `recruiting_class`, `grade`, `links`, `birth_city`, `birth_state`, `high_school_id`, `high_school_name`, `high_school_state`, `slug`, position fields, `linked`, `schools`, `status_id`, `status_name`, and `rank`. Methods: `_set_recruit_data()` loads data, `to_dict()` returns raw JSON, and `__repr__()` provides a representation. | Recruit class |
| **Recruiting rankings** | `Client.get_recruiting_rankings(season, max_pages=None)` returns a list of `Recruit` objects for a given season. | Client class |
| **Ref (various)** | Generic attribute used across objects (e.g., `ref` in `Line`, `Manufacturer`, `Image`). It usually stores the API URL or unique reference to the resource. | Line, Manufacturer, Image classes |
| **Result (Drive)** | Result of a drive (e.g., touchdown, field goal). Stored in `result` and displayed via `result_display`. | Drive class |
| **Rounds (DraftPick)** | The draft round number is stored in `round_number`. | DraftPick class |

### S–W

| Element | Description and callable details | Official sources |
|---|---|---|
| **Schedule** | Represents a league schedule. Attributes: `schedule_list`, `schedule_type`, `season`, and an internal `weeks` list or dictionary. Methods: `get_events(week_num)` returns events for a week (for weekly schedules), `to_dict()` returns raw JSON, and helper methods `_set_schedule_weekly_data()` and `_set_schedule_daily_data()` construct the schedule depending on the schedule type. | Schedule class |
| **ScheduleTypeUnknownError** | Exception raised when the schedule type cannot be determined (neither weekly nor daily). | Exceptions module |
| **Scoring play (Play)** | Boolean attribute indicating whether the play resulted in a score. | Play class |
| **Season team stats** | `Client.get_season_team_stats(season)` returns statistics for every team in the league for a given season. | Client class |
| **Short name (Team/Player/League)** | Concise name for the object. Accessible via `Team.short_display_name`, `Player.short_name`, and `League.short_name`. | Team, Player, League classes |
| **Spread odds (Odds/OddsBet365)** | Betting odds for the point spread. Stored in the `spread_odds` attribute of `Odds` and `OddsBet365`. | Odds and OddsBet365 classes |
| **Standings** | Represented by the `Standings` class. Attributes: `standings` (list of standings entries), `standings_type_name`, and internal caches for `this_athlete` and `this_manufacturer`. Methods: `_load_standings_data()` populates the standings by constructing `Record` objects and pulling player or manufacturer details; `to_dict()` returns raw JSON; `__repr__()` returns a string. | Standings class |
| **Stat** | Class representing a single statistical entry. Attributes: `category`, `season`, `player_id`, `stat_value`, `stat_type_abbreviation`, `description`, `name`, `type`, `per_game_value`, and `rank`. Methods: `_set_stats_data()` loads data, `to_dict()` returns raw JSON, and `__repr__()` provides a formatted string. | Stat class |
| **Team** | Core class representing a team. Attributes include identification fields (`team_id`, `guid`, `uid`, `location`, `name`, `nickname`, `abbreviation`, `display_name`, `short_display_name`), branding fields (`primary_color`, `alternate_color`), status (`is_active`, `is_all_star`), media (list of `Image` objects as `logos`), venue details (`venue_json`, `home_venue`), and internal caches for `records`, `stats`, `coaches`, `betting`, and `roster`. Methods: `get_player_by_season_id()`, `load_team_season_stats(season)`, `get_team_colors()`, `get_home_venue()`, `get_league()`, `load_season_roster(season)`, `load_season_results(season)`, `load_season_coaches(season)`, `load_season_betting_records(season)`, `to_dict()`. | Team class |
| **Teaser odds (OddsBet365)** | Additional odds provided by the Bet365 provider for teaser bets. | OddsBet365 class |
| **Time elapsed (Drive)** | Attribute giving the elapsed time during the drive. | Drive class |
| **Type (Play/Record)** | In a `Play`, `type` describes the play type (e.g., run, pass). In a `Record`, `type` indicates the record type (e.g., team, driver). | Play and Record classes |
| **Underdog (Odds)** | Attribute specifying which team is the underdog in the betting odds. | Odds class |
| **Venue** | Class describing a sports venue. Attributes: `venue_id`, `name`, `address_json`, whether the venue has grass (`grass`), whether it is indoor (`indoor`), and a list of `Image` objects (`images`). Methods: `to_dict()` returns raw JSON and `__repr__()` returns `<Venue | name>`. | Venue class |
| **Vehicle** | Class representing a racing vehicle. Attributes: `number`, `manufacturer`, `chassis`, `engine`, `tire`, `team`. Methods: `_set_vehicle_data()` loads data, `to_dict()` returns raw JSON, and `__repr__()` returns a formatted string. | Vehicle class |
| **Week** | Represents a week in a season’s schedule. Attributes: `week_number`, `start_date`, `end_date`, and a list of `events`. Methods: `get_events()` returns the week’s events; internal methods `_set_week_data()` and `_set_week_datav2()` build the week using concurrent API calls. | Week class |

---

## Glossary

This glossary explains common terms and objects used throughout PyESPN.
Readers can refer to the index above to find where each item is implemented in the code.

- **Athlete** — A general term for a sports player. In PyESPN, athletes are represented by the `Player` class and, in recruiting contexts, by the `Recruit` class.  
- **Bet** — A wager on a sporting event. PyESPN models betting through classes like `BetValue`, `Betting`, `GameOdds`, `Odds`, `OddsBet365`, and `OddsType`.  
- **Betting Provider** — A sportsbook or source of betting odds (e.g., “consensus,” “Bet365”). Providers determine how odds data is parsed and represented.  
- **Draft** — An annual process by which professional sports leagues assign rights to players. In PyESPN the draft is represented by `DraftPick` objects and accessed via `Client.load_year_draft()`.  
- **Drive** — A series of plays executed by one team without surrendering possession. Represented by the `Drive` class.  
- **Event** — A single sports contest (e.g., a game, race). The `Event` class wraps all metadata, teams, odds, drives, and plays for a contest.  
- **Futures** — Bets placed on events that will occur in the future, such as a team winning a championship. PyESPN retrieves futures via `League.betting_futures` and `Client.load_seasons_futures()`.  
- **Line** — A specific betting proposition (e.g., point spread) offered by a provider. Represented by the `Line` class.  
- **Odds** — The probability or payout for a bet. PyESPN models odds via the `Odds` and `OddsBet365` classes, and further breaks them down into `OddsType` (open, current, close).  
- **Play** — An individual action during a game, such as a pass or field goal. The `Play` class stores all relevant details for each play in the play‑by‑play.  
- **Recruit** — A high‑school athlete being recruited by colleges. In PyESPN, recruits are represented by the `Recruit` class and can be retrieved via `Client.get_recruiting_rankings()`.  
- **Schedule** — List of events for a league over a season. The `Schedule` class encapsulates weekly or daily schedules and provides access to `Week` objects.  
- **Standing** — A record of wins, losses, points, etc., for teams or competitors within a league. The `Standings` class contains these records as `Record` objects.  
- **Stat** — A numerical measurement describing player or team performance. The `Stat` class stores an individual statistic, while `Team`, `Player`, and `League` aggregate statistics collections.  
- **Team** — A sports franchise or club. The `Team` class includes identity, branding, venue, roster, coaching, and betting information.  
- **Venue** — A stadium or location where events are held. Represented by the `Venue` class.  
- **Week** — A segment of the sports season used in scheduling. The `Week` class stores events for a given week and provides methods to retrieve them.  
- **Vehicle** — In motorsports contexts, the car or vehicle used by a competitor. The `Vehicle` class captures details like chassis and engine.  

---

## Exception Summary

PyESPN defines several custom exceptions to provide clearer error handling:

- **API400Error** — Raised when ESPN’s API returns a 400 (Bad Request) response.  
- **NoDataReturnedError** — Raised when an API request returns no data.  
- **JSONNotProvidedError** — Raised when a method expecting JSON input does not receive it.  
- **InvalidLeagueError** — Raised when an invalid league abbreviation is passed to the `Client` constructor.  
- **LeagueNotAvailableError** — Raised when the requested league is available in ESPN’s API but not yet supported by PyESPN.  
- **LeagueNotSupportedError** — Raised when a league is not supported by PyESPN.  
- **ScheduleTypeUnknownError** — Raised when the schedule type (weekly/daily) cannot be determined.  

---

## Conclusion

This index and glossary should serve as a detailed reference for developers using the PyESPN library. All
entries are derived from the official documentation and source code. For further details or updates, consult
the PyESPN documentation or inspect the source code directly. 

### References
- Exceptions — https://enderlocke.github.io/pyespn/exceptions/  
- Player — https://enderlocke.github.io/pyespn/classes/player_class/  
- Leader Category — https://enderlocke.github.io/pyespn/classes/leader_category_class/  
- Client — https://enderlocke.github.io/pyespn/pyespn/  
- Event — https://enderlocke.github.io/pyespn/classes/event_class/  
- Betting — https://enderlocke.github.io/pyespn/classes/betting_class/  
- League — https://enderlocke.github.io/pyespn/classes/league_class/  
- Bet Value — https://enderlocke.github.io/pyespn/classes/bet_value_class/  
- Client (api_mapping) — https://enderlocke.github.io/pyespn/pyespn/%23pyespn.core.client.PYESPN.api_mapping  
- Vehicle — https://enderlocke.github.io/pyespn/classes/vehicle_class/  
- Play — https://enderlocke.github.io/pyespn/classes/play_class/  
- Circuit — https://enderlocke.github.io/pyespn/classes/circuit_class/  
- Competition — https://enderlocke.github.io/pyespn/classes/competition_class/  
- Team — https://enderlocke.github.io/pyespn/classes/teams_class/  
- Draft — https://enderlocke.github.io/pyespn/classes/draft_class/  
- Drive — https://enderlocke.github.io/pyespn/classes/drive_class/  
- Recruit — https://enderlocke.github.io/pyespn/classes/recruit_class/  
- Game Odds — https://enderlocke.github.io/pyespn/classes/game_odds_class/  
- Image — https://enderlocke.github.io/pyespn/classes/image_class/  
- Line — https://enderlocke.github.io/pyespn/classes/line_class/  
- Manufacturer — https://enderlocke.github.io/pyespn/classes/manufacturer_class/  
- Odds — https://enderlocke.github.io/pyespn/classes/odds_class/  
- Odds Bet365 — https://enderlocke.github.io/pyespn/classes/odds_bet365_class/  
- Odds Type — https://enderlocke.github.io/pyespn/classes/odds_type_class/  
- Stats — https://enderlocke.github.io/pyespn/classes/stat_class/  
- Record — https://enderlocke.github.io/pyespn/classes/record_class/  
- Schedule — https://enderlocke.github.io/pyespn/classes/schedule_class/  
- Standings — https://enderlocke.github.io/pyespn/classes/standings_class/  
- Venue — https://enderlocke.github.io/pyespn/classes/venue_class/  
- Week — https://enderlocke.github.io/pyespn/classes/week_class/  
