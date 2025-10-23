import styles from "../styles/home.module.css";

export default function HomePage() {
  return (
    <main className={styles.container}>
      <div className={styles.panel}>
        <h1>RosterPilot</h1>
        <p>
          Yahoo Fantasy Football companion scaffolding. Connect Yahoo read-only data with PyESPN game
          feeds to unlock live context and lineup optimization. Frontend implementation will evolve in
          later phases.
        </p>
      </div>
    </main>
  );
}
