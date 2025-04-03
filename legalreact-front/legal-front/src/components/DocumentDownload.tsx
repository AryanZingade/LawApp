import React from "react";

const DocumentDownload = () => {
  const downloadDocument = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/generate_document", {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to download document");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "Generated_Document.docx";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading document:", error);
    }
  };

  return (
    <button
      onClick={downloadDocument}
      style={{
        padding: "10px",
        borderRadius: "8px",
        backgroundColor: "#007bff",
        color: "white",
        border: "none",
        cursor: "pointer",
        fontSize: "16px",
        marginTop: "10px", // Ensures spacing under ResponseBox
      }}
    >
      Download Document
    </button>
  );
};

export default DocumentDownload;
