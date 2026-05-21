import { Line } from "react-chartjs-2";
import {
    Chart as ChartJS,
    LineElement,
    PointElement,
    LinearScale,
    CategoryScale,
    Tooltip,
    Filler,
} from "chart.js";

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler);

export default function ClinicalChart({ chartData, onClose }) {
    if (!chartData || chartData.length === 0) {
        return null;
    }

    const labels = chartData.map((d, i) => {
        const date = new Date(d.data);
        if (isNaN(date.getTime())) return `${i + 1}`;
        return `${date.getDate()}/${date.getMonth() + 1} ${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
    });

    const scores = chartData.map(d => d.score);
    
    const pointColors = scores.map(s => {
        if (s >= 80) return "#f7768e";
        if (s >= 55) return "#ff9f43";
        if (s >= 30) return "#7aa2f7";
        return "#73daca";
    });

    const config = {
        labels,
        datasets: [{
            label: "Scor Risc",
            data: scores,
            borderColor: "#7aa2f7",
            borderWidth: 2,
            pointBackgroundColor: pointColors,
            pointBorderColor: "#0a0b10",
            pointBorderWidth: 1.5,
            pointRadius: 5,
            pointHoverRadius: 8,
            tension: 0.3,
            fill: true,
            backgroundColor: "rgba(122, 162, 247, 0.08)",
        }]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: "#0d0f18",
                titleColor: "#7aa2f7",
                bodyColor: "#c0caf5",
                borderColor: "#1f2335",
                borderWidth: 1,
                callbacks: {
                    label: (ctx) => {
                        const item = chartData[ctx.dataIndex];
                        return `Scor: ${ctx.parsed.y}% - ${item?.category || ""}`;
                    }
                }
            }
        },
        scales: {
            y: {
                min: 0,
                max: 100,
                ticks: {
                    color: "#565f89",
                    stepSize: 25,
                    callback: (v) => v + "%"
                },
                grid: {
                    color: (context) => {
                        if (context.tick.value === 75) return "rgba(247, 118, 142, 0.2)";
                        if (context.tick.value === 50) return "rgba(255, 159, 67, 0.15)";
                        return "#161925";
                    }
                }
            },
            x: {
                ticks: {
                    color: "#565f89",
                    maxRotation: 45,
                    minRotation: 45,
                    autoSkip: true,
                    maxTicksLimit: 8
                },
                grid: { display: false }
            }
        }
    };

    const minWidth = Math.max(500, chartData.length * 50);

    return (
        <div className="chartModal">
            <div className="chartModalContent">
                <div className="chartModalHeader">
                    <span>📊 Evoluție risc</span>
                    {onClose && (
                        <button className="chartCloseBtn" onClick={onClose}>✕</button>
                    )}
                </div>
                <div className="chartModalBody">
                    <div style={{ minWidth: `${minWidth}px`, height: "300px" }}>
                        <Line data={config} options={chartOptions} />
                    </div>
                </div>
                <div className="chartModalFooter">
                    <span className="legendBadge critical">Urgență</span>
                    <span className="legendBadge high">Ridicat</span>
                    <span className="legendBadge mid">Stres</span>
                    <span className="legendBadge low">Neutru</span>
                </div>
            </div>
        </div>
    );
}