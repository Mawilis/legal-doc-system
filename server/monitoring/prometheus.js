#!/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ PROMETHEUS METRICS REGISTRY                                               ║
  ║ Lightweight metrics collection for /metrics endpoint                     ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

export class PrometheusRegistry {
  constructor() {
    this.counters = new Map();
    this.gauges = new Map();
    this.histograms = new Map();
    this.contentType = 'text/plain; version=0.0.4';
  }

  createCounter(name, help) {
    this.counters.set(name, { value: 0, help });
  }

  incrementCounter(name, inc = 1) {
    const counter = this.counters.get(name);
    if (counter) {
      counter.value += inc;
    }
  }

  createGauge(name, help) {
    this.gauges.set(name, { value: 0, help });
  }

  setGauge(name, value) {
    const gauge = this.gauges.get(name);
    if (gauge) {
      gauge.value = value;
    }
  }

  createHistogram(name, help, buckets = [0.1, 0.5, 1, 2.5, 5, 10]) {
    this.histograms.set(name, {
      buckets,
      counts: new Array(buckets.length + 1).fill(0),
      sum: 0,
      count: 0,
      help,
    });
  }

  observeHistogram(name, value) {
    const hist = this.histograms.get(name);
    if (!hist) return;

    hist.sum += value;
    hist.count++;

    // Find bucket
    let bucketIndex = hist.buckets.length;
    for (let i = 0; i < hist.buckets.length; i++) {
      if (value <= hist.buckets[i]) {
        bucketIndex = i;
        break;
      }
    }
    hist.counts[bucketIndex]++;
  }

  async metrics() {
    let output = '';

    // Format counters
    for (const [name, counter] of this.counters) {
      output += `# HELP ${name} ${counter.help}\n`;
      output += `# TYPE ${name} counter\n`;
      output += `${name} ${counter.value}\n\n`;
    }

    // Format gauges
    for (const [name, gauge] of this.gauges) {
      output += `# HELP ${name} ${gauge.help}\n`;
      output += `# TYPE ${name} gauge\n`;
      output += `${name} ${gauge.value}\n\n`;
    }

    // Format histograms
    for (const [name, hist] of this.histograms) {
      output += `# HELP ${name} ${hist.help}\n`;
      output += `# TYPE ${name} histogram\n`;

      // Buckets
      for (let i = 0; i < hist.buckets.length; i++) {
        output += `${name}_bucket{le="${hist.buckets[i]}"} ${hist.counts[i]}\n`;
      }
      output += `${name}_bucket{le="+Inf"} ${hist.counts[hist.counts.length - 1]}\n`;

      // Count and sum
      output += `${name}_count ${hist.count}\n`;
      output += `${name}_sum ${hist.sum}\n\n`;
    }

    // Add process metrics
    output += `# HELP process_start_time_seconds Start time of the process\n`;
    output += `# TYPE process_start_time_seconds gauge\n`;
    output += `process_start_time_seconds ${Math.floor(Date.now() / 1000)}\n\n`;

    output += `# HELP process_memory_bytes Process memory usage\n`;
    output += `# TYPE process_memory_bytes gauge\n`;
    const mem = process.memoryUsage();
    output += `process_memory_bytes{type="rss"} ${mem.rss}\n`;
    output += `process_memory_bytes{type="heapTotal"} ${mem.heapTotal}\n`;
    output += `process_memory_bytes{type="heapUsed"} ${mem.heapUsed}\n`;
    output += `process_memory_bytes{type="external"} ${mem.external}\n\n`;

    return output;
  }
}

export default PrometheusRegistry;
