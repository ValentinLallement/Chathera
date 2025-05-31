export default function HomePage() {
  return (
    <div>
      <h1>HomePage</h1>
      <p>This is a test page to check scrolling functionality.</p>
      {Array.from({ length: 100 }, (_, i) => (
        <p key={i}>This is line number {i + 1}</p>
      ))}
    </div>
  );
}
