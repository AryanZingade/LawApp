import React from "react";

function ResponseBox({ response }: { response: any }) {
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
    <div style={styles.responseContainer}>
      <h3>Response from Flask:</h3>
      {typeof response === "object" ? (
        <div>{renderJson(response)}</div>
      ) : (
        <p>{response}</p>
      )}
    </div>
  );
}

const styles = {
  responseContainer: {
    padding: "10px",
    border: "1px solid #ccc",
    borderRadius: "12px",
    width: "1000px",
    minHeight: "250px",
    backgroundColor: "#f9f9f9",
    marginTop: "10px",
    maxHeight: "350px",
    overflowY: "auto",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  } as const,
};

export default ResponseBox;
