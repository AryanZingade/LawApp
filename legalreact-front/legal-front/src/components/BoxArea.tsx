import React, { useState } from "react";
import axios from "axios";

function BoxArea() {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [response, setResponse] = useState<any>(null);
  const [targetLanguage, setTargetLanguage] = useState("en"); // Default language

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleUpload = async (
    e: React.ChangeEvent<HTMLInputElement>,
    type: "summarize" | "translate"
  ) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      uploadFile(selectedFile, type);
    }
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

  const uploadFile = async (
    selectedFile: File,
    type: "summarize" | "translate"
  ) => {
    const formData = new FormData();
    formData.append("file", selectedFile);
    if (type === "translate") {
      formData.append("target_language", targetLanguage);
    }
    const route = type === "summarize" ? "summarize" : "translatedoc";
    try {
      const response = await axios.post(
        `http://127.0.0.1:5000/${route}`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setResponse(response.data);
    } catch (error) {
      console.error(`Error uploading file to ${route}:`, error);
    }
  };

  const renderJson = (data: any) => {
    if (!data || typeof data !== "object") return <p>{String(data)}</p>;
    return Object.entries(data).map(([key, value]) => (
      <div key={key}>
        <strong>{key}:</strong>{" "}
        {Array.isArray(value) ? (
          <ul style={{ marginLeft: "15px" }}>
            {value.map((item, index) => (
              <li key={index}>
                {typeof item === "object" ? renderJson(item) : item}
              </li>
            ))}
          </ul>
        ) : typeof value === "object" ? (
          <div style={{ marginLeft: "15px" }}>{renderJson(value)}</div>
        ) : (
          ` ${String(value)}`
        )}
      </div>
    ));
  };

  return (
    <div style={styles.inputContainer}>
      <div style={styles.inputRow}>
        <input
          type="text"
          placeholder="Enter Query"
          value={query}
          onChange={handleQueryChange}
          onKeyDown={(e) => e.key === "Enter" && sendQuery()}
          style={styles.input}
        />

        {/* Summarization Upload Button */}
        <label style={styles.uploadButton}>
          <i className="fas fa-folder" style={styles.pdfIcon}></i>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => handleUpload(e, "summarize")}
            style={styles.fileInput}
          />
        </label>

        {/* Translation Upload Button */}
        <label style={styles.uploadButton}>
          <i className="fas fa-globe" style={styles.pdfIcon}></i>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => handleUpload(e, "translate")}
            style={styles.fileInput}
          />
        </label>
      </div>

      {/* Target Language Dropdown */}
      <select
        value={targetLanguage}
        onChange={(e) => setTargetLanguage(e.target.value)}
        style={styles.dropdown}
      >
        <option value="en">English</option>
        <option value="fr">French</option>
        <option value="de">German</option>
        <option value="es">Spanish</option>
        <option value="zh">Chinese</option>
      </select>

      {/* Response Output Box */}
      {response && (
        <div style={styles.responseContainer}>
          <h3>Response from Flask:</h3>
          {typeof response === "object" ? (
            <div>{renderJson(response)}</div>
          ) : (
            <p>{response}</p>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  inputContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    gap: "10px",
  } as const,

  inputRow: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },

  input: {
    width: "600px",
    padding: "10px",
    fontSize: "16px",
    borderRadius: "10px",
    border: "1.5px solid #ccc",
  },

  uploadButton: {
    width: "40px",
    height: "40px",
    borderRadius: "50%",
    border: "1.5px solid #ccc",
    cursor: "pointer",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },

  pdfIcon: {
    fontSize: "18px",
    color: "#000",
  },

  fileInput: {
    display: "none",
  },

  dropdown: {
    padding: "10px",
    fontSize: "16px",
    borderRadius: "10px",
    border: "1.5px solid #ccc",
    backgroundColor: "#fff",
    cursor: "pointer",
  },

  responseContainer: {
    padding: "10px",
    border: "1px solid #ccc",
    borderRadius: "12px",
    width: "700px",
    minHeight: "250px",
    backgroundColor: "#f9f9f9",
    marginTop: "10px",
    maxHeight: "300px",
    overflowY: "auto",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  } as const,
};

export default BoxArea;
