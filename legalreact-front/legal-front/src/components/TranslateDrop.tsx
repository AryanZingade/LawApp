import React from "react";

function Translate({
  targetLanguage,
  setTargetLanguage,
}: {
  targetLanguage: string;
  setTargetLanguage: (lang: string) => void;
}) {
  return (
    <select
      value={targetLanguage}
      onChange={(e) => setTargetLanguage(e.target.value)}
      style={dropdownStyle}
    >
      <option value="en">English</option>
      <option value="hi">Hindi</option>
    </select>
  );
}

const dropdownStyle = {
  padding: "10px",
  fontSize: "16px",
  borderRadius: "5px",
  border: "1px solid #ccc",
  width: "200px",
};

export default Translate;
