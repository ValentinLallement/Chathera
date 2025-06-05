import toast from "react-hot-toast";
import { useHealth } from "../hooks/useApi";

export default function DemoPage() {
  const { data, isPending, isError, error, isFetching } = useHealth();
  const notify = () =>
    toast.success("Logged In", {
      style: {
        borderRadius: "10px",
        background: "#1f1f1f",
        border: "1px solid #333",
        boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
        color: "#fff",
        padding: "12px 16px",
        fontSize: "0.95rem",
      },
    });

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
      <button onClick={notify} className="bg-amber-700">
        Make me a toast
      </button>
    </div>
  );
}
