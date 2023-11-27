import React, { useState, useEffect } from "react";
import axios from "axios";

const SearchComponent = () => {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (loading) {
        setResult("");
    }
  }, [loading])

  const handleSearch = async () => {
    setLoading(true);

    try {
      const response = await axios.post("http://localhost:80/ask", { query });

      setResult(response.data.answer);
      setError("");
    } catch (err) {
      console.error(err);
      setError("An error occurred while fetching results.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="search-area">
        <textarea
          rows="20"
          value={query}
          onChange={(e) =>
            setQuery(
              e.target.value
                .replaceAll(".\n", ". ")
                .replaceAll(/(question \d+)/gi, "")
            )
          }
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? "Answering..." : "Ask"}
        </button>
      </div>
      <div className="search-results">
        {error && <p>{error}</p>}
        {result.split("\n").map((line, idx) => (
          <p key={idx}>{line}</p>
        ))}
      </div>
    </>
  );
};

export default SearchComponent;
