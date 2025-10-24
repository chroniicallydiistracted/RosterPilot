"use client";

import clsx from "clsx";

import styles from "./ProvenanceBadge.module.css";

interface ProvenanceBadgeProps {
  source: "yahoo" | "pyespn" | "optimizer";
  label?: string;
}

const SOURCE_COPY: Record<string, string> = {
  yahoo: "Yahoo data",
  pyespn: "PyESPN feed",
  optimizer: "Optimizer"
};

export function ProvenanceBadge({ source, label }: ProvenanceBadgeProps) {
  const text = label ?? SOURCE_COPY[source] ?? source;
  return <span className={clsx(styles.badge, styles[source])}>{text}</span>;
}
