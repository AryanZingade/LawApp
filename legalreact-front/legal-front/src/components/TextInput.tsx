import React, { useState } from "react";
import axios from "axios";

function TextInput({ setResponse }: { setResponse: (data: any) => void }) {
  const [query, setQuery] = useState("");

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const sendQuery = async () => {
    if (!query.trim()) return;
    try {
      const res = await axios.post("http://127.0.0.1:5000/invoke", {
        user_input: query,
      });
      setResponse(res.data);
    } catch (error) {
      console.error("Error sending query:", error);
      setResponse("Error fetching response.");
    }
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Enter Query"
        value={query}
        onChange={handleQueryChange}
        onKeyDown={(e) => e.key === "Enter" && sendQuery()}
        style={{
          width: "600px",
          padding: "10px",
          fontSize: "16px",
          borderRadius: "10px",
          border: "1.5px solid #ccc",
        }}
      />
    </div>
  );
}

export default TextInput;
