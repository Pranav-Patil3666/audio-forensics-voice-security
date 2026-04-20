export class RiskEngine {
  private history: number[] = [];
  private maxHistory = 5;

  /**
   * Add new prediction and compute risk
   */
  addPrediction(fakeProb: number) {
    this.history.push(fakeProb);

    // keep sliding window
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }

    return this.getRisk();
  }

  /**
   * Compute risk based on rolling average
   */
  getRisk() {
    if (this.history.length === 0) return "LOW";

    const avg =
      this.history.reduce((a, b) => a + b, 0) / this.history.length;

    if (avg > 0.85) return "HIGH";
    if (avg > 0.65) return "MEDIUM";
    return "LOW";
  }

  /**
   * Debug info
   */
  getStats() {
    const avg =
      this.history.reduce((a, b) => a + b, 0) / this.history.length;

    return {
      history: this.history,
      avg: avg || 0,
    };
  }
}