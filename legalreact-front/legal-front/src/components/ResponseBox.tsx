import React from "react";
import { Card, Heading, Text } from "@radix-ui/themes";

function ResponseBox({ response }: { response: any }) {
  const renderJson = (data: any) => {
    if (!data || typeof data !== "object") return <Text>{String(data)}</Text>;

    return Object.entries(data).map(([key, value]) => (
      <div key={key} style={{ marginBottom: "10px" }}>
        <Text as="span" weight="bold">
          {key}:
        </Text>{" "}
        {Array.isArray(value) ? (
          <ul style={{ marginLeft: "20px" }}>
            {value.map((item, index) => (
              <li key={index}>
                {typeof item === "object" ? (
                  renderJson(item)
                ) : (
                  <Text>{item}</Text>
                )}
              </li>
            ))}
          </ul>
        ) : typeof value === "object" ? (
          <div style={{ marginLeft: "20px" }}>{renderJson(value)}</div>
        ) : (
          <Text> {String(value)}</Text>
        )}
      </div>
    ));
  };

  return (
    <Card
      size="3"
      style={{
        width: "1000px",
        minHeight: "250px",
        maxHeight: "450px",
        overflowY: "auto",
        backgroundColor: "#f9f9f9",
        marginTop: "20px",
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
      }}
    >
      <Heading size="4" mb="3">
        Response from Flask:
      </Heading>
      {typeof response === "object" ? (
        <div>{renderJson(response)}</div>
      ) : (
        <Text>{response}</Text>
      )}
    </Card>
  );
}

export default ResponseBox;
