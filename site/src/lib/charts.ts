// Server-generated inline SVG charts (AD-8, UX-DR1): no charting library, no client JS.
// Each function returns an SVG string rendered into the page at build time.

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

interface Bar { label: string; value: number; }

export function barChart(data: Bar[], opts: { accent?: string; title?: string; ticks?: number } = {}): string {
  const accent = opts.accent ?? '#3a4f9c';
  const W = 720, H = 180, padL = 8, padR = 8, padT = 12, padB = 22;
  if (!data.length) return '';
  const maxV = Math.max(1, ...data.map((d) => d.value));
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const bw = plotW / data.length;
  const bars = data.map((d, i) => {
    const h = Math.max(0, (d.value / maxV) * plotH);
    const x = padL + i * bw;
    const y = padT + (plotH - h);
    return `<rect x="${(x + bw * 0.12).toFixed(2)}" y="${y.toFixed(2)}" width="${(bw * 0.76).toFixed(2)}" height="${h.toFixed(2)}" fill="${accent}"><title>${esc(d.label)}: ${d.value}</title></rect>`;
  }).join('');
  // sparse x labels: first, last, and year boundaries
  const labels = data.map((d, i) => {
    const isYear = d.label.endsWith('-01');
    if (i === 0 || i === data.length - 1 || isYear) {
      const x = padL + i * bw + bw / 2;
      const text = d.label.length >= 7 ? d.label.slice(0, 4) : d.label;
      return `<text x="${x.toFixed(1)}" y="${H - 6}" text-anchor="middle" class="chart-axis">${esc(text)}</text>`;
    }
    return '';
  }).join('');
  const baseline = `<line x1="${padL}" y1="${padT + plotH}" x2="${W - padR}" y2="${padT + plotH}" class="chart-baseline" />`;
  return `<svg viewBox="0 0 ${W} ${H}" class="chart" role="img" aria-label="${esc(opts.title ?? 'bar chart')}" preserveAspectRatio="none">${baseline}${bars}${labels}</svg>`;
}

interface Cell { date: string; commits: number; }

export function heatmap(cells: Cell[], opts: { accent?: string; weeks?: number } = {}): string {
  if (!cells.length) return '';
  const accent = opts.accent ?? '#3a4f9c';
  const weeks = opts.weeks ?? 53;
  const byDate = new Map(cells.map((c) => [c.date, c.commits]));
  const maxV = Math.max(1, ...cells.map((c) => c.commits));
  // end at the latest cell date; align the grid end to the end of that week (Saturday)
  const end = new Date(cells[cells.length - 1].date + 'T00:00:00Z');
  end.setUTCDate(end.getUTCDate() + (6 - end.getUTCDay()));
  const start = new Date(end);
  start.setUTCDate(start.getUTCDate() - (weeks * 7 - 1));

  const cellSize = 11, gap = 2.5, step = cellSize + gap, padTop = 16, padLeft = 4;
  const shade = (v: number): string => {
    if (v <= 0) return '#ebedf0';
    const t = v / maxV;
    if (t > 0.66) return accent;
    if (t > 0.33) return accent + 'b3'; // ~70% alpha
    return accent + '66';               // ~40% alpha
  };
  let rects = '', col = 0, monthLabels = '', lastMonth = -1;
  const d = new Date(start);
  while (d <= end) {
    const x = padLeft + col * step;
    const row = d.getUTCDay();
    const iso = d.toISOString().slice(0, 10);
    const v = byDate.get(iso) ?? 0;
    rects += `<rect x="${x.toFixed(1)}" y="${(padTop + row * step).toFixed(1)}" width="${cellSize}" height="${cellSize}" rx="2" fill="${shade(v)}"><title>${iso}: ${v} commit${v === 1 ? '' : 's'}</title></rect>`;
    if (row === 0) {
      const m = d.getUTCMonth();
      if (m !== lastMonth) {
        const name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][m];
        monthLabels += `<text x="${x.toFixed(1)}" y="10" class="chart-axis">${name}</text>`;
        lastMonth = m;
      }
    }
    if (row === 6) col++;
    d.setUTCDate(d.getUTCDate() + 1);
  }
  const W = padLeft + (col + 1) * step, H = padTop + 7 * step;
  return `<svg viewBox="0 0 ${W} ${H}" class="heatmap" role="img" aria-label="Daily commit intensity, trailing ${weeks} weeks">${monthLabels}${rects}</svg>`;
}
