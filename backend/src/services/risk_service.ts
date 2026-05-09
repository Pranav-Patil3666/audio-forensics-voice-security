export class RiskEngine {

  private history: number[] = [];
  private maxWindow = 5;

  private smoothedScore: number | null = null;
  private previousRisk = "LOW";

  // calibrated thresholds
  private HIGH_THRESHOLD = 0.80;
  private MEDIUM_THRESHOLD = 0.50;

  addPrediction(fakeProb: number) {

    
    // 1. CLIP EXTREME NOISE
    
    fakeProb = Math.max(0, Math.min(1, fakeProb));

    
    // 2. UPDATE HISTORY
    
    this.history.push(fakeProb);

    if (this.history.length > this.maxWindow) {
      this.history.shift();
    }

    
    // 3. EMA SMOOTHING
    
    if (this.smoothedScore === null) {

      this.smoothedScore = fakeProb;

    } else {

      this.smoothedScore =
        0.7 * fakeProb +
        0.3 * this.smoothedScore;
    }

    
    // 4. CONSISTENCY
    
    const mediumCount =
      this.history.filter(
        (v) => v >= this.MEDIUM_THRESHOLD
      ).length;

    const highCount =
      this.history.filter(
        (v) => v >= this.HIGH_THRESHOLD
      ).length;

    
    // 5. STRONG FAKE AVERAGE
    
    const avg =
      this.history.reduce((a, b) => a + b, 0)
      / this.history.length;

    
    // 6. SPIKE DETECTION
    
    let spike = false;

    if (this.history.length >= 2) {

      const last =
        this.history[this.history.length - 1];

      const prev =
        this.history[this.history.length - 2];

      if (Math.abs(last - prev) > 0.45) {
        spike = true;
      }
    }

    
    // 7. FINAL DECISION
    
    let risk = "LOW";

    // persistent strong fake
    if (
      highCount >= 3 &&
      avg >= 0.75
    ) {

      risk = "HIGH";
    }

    // sustained suspicion
    else if (
      mediumCount >= 2 ||
      (this.smoothedScore ?? 0) >= 0.55
    ) {

      risk = "MEDIUM";
    }

    // isolated spikes
    if (
      spike &&
      risk === "LOW"
    ) {

      risk = "MEDIUM";
    }

    
    // 8. HYSTERESIS
    
    if (
      this.previousRisk === "HIGH" &&
      risk === "MEDIUM" &&
      (this.smoothedScore ?? 0) > 0.45
    ) {

      risk = "HIGH";
    }

    this.previousRisk = risk;

    return risk;
  }

  getStats() {

    return {
      history: this.history,
      smoothed: this.smoothedScore,
      previousRisk: this.previousRisk,
    };
  }
}