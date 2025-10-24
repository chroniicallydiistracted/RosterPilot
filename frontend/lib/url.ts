const stripTrailingSlashes = (value: string): string => value.replace(/\/+$/, "");

export const trimTrailingSlash = (value: string): string => {
  if (!value) {
    return value;
  }
  return stripTrailingSlashes(value);
};

export const ensureLeadingSlash = (value: string): string => {
  if (!value) {
    return "/";
  }
  return value.startsWith("/") ? value : `/${value}`;
};

export const buildApiUrl = (baseUrl: string, path: string, prefix = "/api"): string => {
  const normalizedBase = trimTrailingSlash(baseUrl);
  const normalizedPrefix = prefix ? ensureLeadingSlash(prefix).replace(/\/+$/, "") : "";
  const normalizedPath = ensureLeadingSlash(path);
  return `${normalizedBase}${normalizedPrefix}${normalizedPath}`;
};

export const buildWebSocketUrl = (baseUrl: string, path: string): string => {
  const base = new URL(trimTrailingSlash(baseUrl));
  const basePath = trimTrailingSlash(base.pathname || "");
  const normalizedPath = ensureLeadingSlash(path);
  const dedupedPath = basePath && normalizedPath.startsWith(`${basePath}/`)
    ? normalizedPath.slice(basePath.length)
    : normalizedPath;
  base.pathname = `${basePath}${dedupedPath}` || "/";
  return trimTrailingSlash(base.toString());
};
