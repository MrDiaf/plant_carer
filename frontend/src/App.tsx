import { CSSProperties, useEffect, useMemo, useState } from "react";
import { Plant, getPlant, replacePlant, waterPlant } from "./api";

const FLOWER_COLORS: Record<string, string> = {
  red: "#e84d4f",
  pink: "#f08ab2",
  purple: "#8c5bd6",
  blue: "#4a90d9",
  yellow: "#f2c94c",
  orange: "#f2994a",
  white: "#fffaf0"
};

function formatDateTime(value: string | null): string {
  if (!value) {
    return "Never watered";
  }

  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function formatDurationUntil(target: string, now: number): string {
  const difference = new Date(target).getTime() - now;

  if (difference <= 0) {
    return "now";
  }

  const totalMinutes = Math.ceil(difference / 60000);
  const days = Math.floor(totalMinutes / 1440);
  const hours = Math.floor((totalMinutes % 1440) / 60);
  const minutes = totalMinutes % 60;

  if (days > 0) {
    return `${days}d ${hours}h`;
  }

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }

  return `${minutes}m`;
}

function stateLabel(state: Plant["state"]): string {
  return state.charAt(0).toUpperCase() + state.slice(1);
}

function PlantVisual({ plant }: { plant: Plant }) {
  const flowerColor = plant.bloom_color
    ? FLOWER_COLORS[plant.bloom_color] ?? plant.bloom_color
    : "#f08ab2";

  return (
    <div
      className={`plant-visual plant-${plant.state}`}
      style={{ "--flower-color": flowerColor } as CSSProperties}
      aria-label={`Plant state: ${plant.state}`}
      role="img"
    >
      <div className="plant-art">
        <div className="flower-head">
          <span className="petal petal-one" />
          <span className="petal petal-two" />
          <span className="petal petal-three" />
          <span className="petal petal-four" />
          <span className="flower-center" />
        </div>
        <span className="stem stem-main" />
        <span className="stem stem-left" />
        <span className="stem stem-right" />
        <span className="leaf leaf-left" />
        <span className="leaf leaf-right" />
        <span className="leaf leaf-back-left" />
        <span className="leaf leaf-back-right" />
        <span className="soil" />
        <span className="pot-lip" />
        <span className="pot" />
      </div>
    </div>
  );
}

function App() {
  const [plant, setPlant] = useState<Plant | null>(null);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState<"water" | "replace" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [now, setNow] = useState(Date.now());

  async function loadPlant() {
    setError(null);
    try {
      const currentPlant = await getPlant();
      setPlant(currentPlant);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load the plant.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPlant();
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 30000);
    return () => window.clearInterval(timer);
  }, []);

  const timeline = useMemo(() => {
    if (!plant) {
      return null;
    }

    if (plant.state === "dead") {
      return {
        thirsty: "Dried out",
        death: "Died",
        bloom: formatDateTime(plant.bloom_at)
      };
    }

    if (plant.state === "bloomed") {
      return {
        thirsty: "Complete",
        death: "Complete",
        bloom: "Bloomed"
      };
    }

    return {
      thirsty:
        plant.state === "thirsty"
          ? "Thirsty now"
          : `Thirsty in ${formatDurationUntil(plant.thirsty_at, now)}`,
      death: `Dies in ${formatDurationUntil(plant.dies_at, now)}`,
      bloom: formatDateTime(plant.bloom_at)
    };
  }, [plant, now]);

  async function runAction(kind: "water" | "replace") {
    setError(null);
    setAction(kind);

    try {
      const nextPlant = kind === "water" ? await waterPlant() : await replacePlant();
      setPlant(nextPlant);
      setNow(Date.now());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The plant did not respond.");
      await loadPlant();
    } finally {
      setAction(null);
    }
  }

  const showReplace = plant?.state === "dead" || plant?.state === "bloomed";
  const waterDisabled = !plant || !plant.can_water || action !== null;

  return (
    <main className="page-shell">
      <section className="phone-card" aria-live="polite">
        <header className="app-header">
          <p className="eyebrow">Daily plant care</p>
          <h1>Pocket Sprout</h1>
        </header>

        {loading ? (
          <div className="loading-state">Loading your plant...</div>
        ) : plant ? (
          <>
            <PlantVisual plant={plant} />

            <section className="status-section">
              <div>
                <p className="state-kicker">Current state</p>
                <h2>{stateLabel(plant.state)}</h2>
              </div>
              <p className="message">{plant.message}</p>
            </section>

            <dl className="plant-facts">
              <div>
                <dt>Days alive</dt>
                <dd>{plant.days_alive}</dd>
              </div>
              <div>
                <dt>Last watered</dt>
                <dd>{formatDateTime(plant.last_watered_at)}</dd>
              </div>
              <div>
                <dt>Water clock</dt>
                <dd>{timeline?.thirsty}</dd>
              </div>
              <div>
                <dt>Safe until</dt>
                <dd>{timeline?.death}</dd>
              </div>
              <div>
                <dt>Bloom day</dt>
                <dd>{timeline?.bloom}</dd>
              </div>
              <div>
                <dt>Flower color</dt>
                <dd className="color-value">
                  {plant.bloom_color ? (
                    <>
                      <span
                        className="color-dot"
                        style={
                          {
                            "--dot-color":
                              FLOWER_COLORS[plant.bloom_color] ?? plant.bloom_color
                          } as CSSProperties
                        }
                      />
                      {plant.bloom_color}
                    </>
                  ) : (
                    "Waiting"
                  )}
                </dd>
              </div>
            </dl>

            {error ? <p className="error-banner">{error}</p> : null}

            <div className="actions">
              <button
                className="primary-action"
                type="button"
                disabled={waterDisabled}
                onClick={() => runAction("water")}
              >
                {action === "water"
                  ? "Watering..."
                  : plant.can_water
                    ? "Water plant"
                    : "Watered today"}
              </button>

              {showReplace ? (
                <button
                  className="secondary-action"
                  type="button"
                  disabled={action !== null}
                  onClick={() => runAction("replace")}
                >
                  {action === "replace" ? "Planting..." : "Replace plant"}
                </button>
              ) : null}
            </div>
          </>
        ) : (
          <div className="empty-state">
            <p>No plant could be loaded.</p>
            {error ? <p className="error-banner">{error}</p> : null}
            <button className="primary-action" type="button" onClick={loadPlant}>
              Try again
            </button>
          </div>
        )}
      </section>
    </main>
  );
}

export default App;
