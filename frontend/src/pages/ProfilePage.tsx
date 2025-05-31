import { useEffect, useState } from "react";
import { useLoading } from "../contexts/LoadingContext";

export default function ProfilePage() {
  const [data, setData] = useState<string[]>([]);
  const { startLoading, stopLoading } = useLoading();

  useEffect(() => {
    const loadData = async () => {
      startLoading();
      await new Promise((resolve) => setTimeout(resolve, 2000));
      const newData = Array.from(
        { length: 1000 },
        (_, i) =>
          `Profile data item ${
            i + 1
          } with some extra text to make it longer and test scrolling behavior`
      );
      setData(newData);
      stopLoading();
    };

    loadData();
  }, [startLoading, stopLoading]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Profile Page</h1>
      <div className="space-y-2">
        {data.map((item, index) => (
          <div key={index} className="p-4 bg-[#222222] rounded shadow">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}
