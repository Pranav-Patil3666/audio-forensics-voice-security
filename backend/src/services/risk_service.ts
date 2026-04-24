export class RiskEngine {
  private history: number[] = [];
  private maxWindow = 5;

  private smoothedScore: number | null = null;

  // thresholds (tune later)
  private HIGH_THRESHOLD = 0.75;
  private MEDIUM_THRESHOLD = 0.5;

  addPrediction(fakeProb: number) {

    // 1. UPDATE HISTORY

    this.history.push(fakeProb);

    if (this.history.length > this.maxWindow) {
      this.history.shift();
    }

    // 2. EXPONENTIAL SMOOTHING

    if (this.smoothedScore === null) {
      this.smoothedScore = fakeProb;
    } else {
      this.smoothedScore = 0.6 * fakeProb + 0.4 * this.smoothedScore;
    }

    // =========================
    // 3. CONSISTENCY LOGIC
    // =========================
    const highFakeCount = this.history.filter(
      (v) => v > this.HIGH_THRESHOLD
    ).length;

    // =========================
    // 4. SPIKE DETECTION
    // =========================
    let spike = false;

    if (this.history.length >= 2) {
      const last = this.history[this.history.length - 1];
      const prev = this.history[this.history.length - 2];

      if (Math.abs(last - prev) > 0.5) {
        spike = true;
      }
    }


    // 5. FINAL RISK DECISION

    let risk = "LOW";

    // strong signal
    if (highFakeCount >= 3) {
      risk = "HIGH";
    }
    // medium signal
    else if (this.smoothedScore > this.MEDIUM_THRESHOLD) {
      risk = "MEDIUM";
    }

    // spike increases suspicion
    if (spike && risk === "LOW") {
      risk = "MEDIUM";
    }

    return risk;
  }

  getStats() {
    return {
      history: this.history,
      smoothed: this.smoothedScore,
    };
  }
}