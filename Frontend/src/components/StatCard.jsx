export default function StatCard({ title, value }) {
  return (
    <div style={styles.card}>
      <h4>{title}</h4>
      <p>{value}</p>
    </div>
  );
}

const styles = {
  card: {
    background: "rgba(255,255,255,0.1)",
    borderRadius: "16px",
    padding: "20px",
    minWidth: "180px",
    textAlign: "center",
    backdropFilter: "blur(10px)",
  },
};
