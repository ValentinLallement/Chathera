import { useHealth } from "../hooks/useApi";

export default function DemoPage() {
  const { data, isPending, isError, error, isFetching } = useHealth();

  if (isPending) return <div className="pt-[200px] text-white">Loading…</div>;
  if (isError)
    return (
      <div className="pt-[200px] text-white">
        Error: {(error as Error).message}
      </div>
    );

  return (
    <div className="pt-[200px]">
      <h3 className="text-white">Backend Health</h3>
      <h2 className="text-bold text-white">status: {data.status}</h2>
      {isFetching && <p>Updating…</p>}
    </div>
  );
}
