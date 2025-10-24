import { buildApiUrl, buildWebSocketUrl, ensureLeadingSlash, trimTrailingSlash } from "@/lib/url";

describe("url helpers", () => {
  it("trims trailing slashes", () => {
    expect(trimTrailingSlash("https://api.example.com//")).toBe("https://api.example.com");
  });

  it("ensures leading slash", () => {
    expect(ensureLeadingSlash("games")).toBe("/games");
    expect(ensureLeadingSlash("/games")).toBe("/games");
  });

  it("builds api urls with prefix", () => {
    expect(buildApiUrl("https://api.example.com", "/me/leagues", "/api")).toBe("https://api.example.com/api/me/leagues");
    expect(buildApiUrl("https://api.example.com/", "games/live", "api")).toBe("https://api.example.com/api/games/live");
  });

  it("builds websocket urls", () => {
    expect(buildWebSocketUrl("wss://api.example.com/ws", "/ws/games/123"))
      .toBe("wss://api.example.com/ws/games/123");
  });
});
