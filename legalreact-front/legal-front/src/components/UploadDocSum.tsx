import React from "react";
import axios from "axios";

function PdfUpload({
  setResponse,
  targetLanguage,
  setDocumentReady, // Receive this prop
}: {
  setResponse: (data: any) => void;
  targetLanguage: string;
  setDocumentReady: (ready: boolean) => void;
}) {
  const handleUpload = async (
    e: React.ChangeEvent<HTMLInputElement>,
    type: "summarize" | "translate"
  ) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];

      const formData = new FormData();
      formData.append("file", selectedFile);
      if (type === "translate")
        formData.append("target_language", targetLanguage);

      const route = type === "summarize" ? "summarize" : "translatedoc";

      try {
        const response = await axios.post(
          `http://127.0.0.1:5000/${route}`,
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );

        setResponse(response.data);
        setDocumentReady(true); // Mark document as ready
      } catch (error) {
        console.error(`Error uploading file to ${route}:`, error);
      }
    }
  };

  return (
    <div style={{ display: "flex", gap: "10px" }}>
      <label style={uploadButtonStyle}>
        <i className="fas fa-folder"></i>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => handleUpload(e, "summarize")}
          style={{ display: "none" }}
        />
      </label>

      <label style={uploadButtonStyle}>
        <i className="fas fa-globe"></i>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => handleUpload(e, "translate")}
          style={{ display: "none" }}
        />
      </label>
    </div>
  );
}

const uploadButtonStyle = {
  width: "40px",
  height: "40px",
  borderRadius: "50%",
  border: "1.5px solid #ccc",
  cursor: "pointer",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  fontSize: "18px",
};

export default PdfUpload;
