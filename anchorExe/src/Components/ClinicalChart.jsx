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

export default function ClinicalChart({ chartData }) {
    if (!chartData || chartData.length === 0) {
        return (
            <div className="chartPanel">
                <div className="cleanEmptyState">Date insuficiente pentru generarea graficului clinic.</div>
            </div>
        );
    }

    // Construim etichetele
    const labels = chartData.map((d, i) => {
        const date = new Date(d.data);
        if (isNaN(date.getTime())) return `#${i + 1}`;
        return `${date.getDate()}/${date.getMonth() + 1} ${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
    });

    const scores = chartData.map(d => d.score);
    
    // Culori pentru puncte
    const pointColors = scores.map(s => {
        if (s >= 80) return "#f7768e";
        if (s >= 55) return "#ff9f43";
        if (s >= 30) return "#7aa2f7";
        return "#73daca";
    });

    // Configurația graficului
    const config = {
        labels,
        datasets: [{
            label: "Indice Risc Clinic",
            data: scores,
            borderColor: "#7aa2f7",
            borderWidth: 2,
            pointBackgroundColor: pointColors,
            pointBorderColor: "#0a0b10",
            pointBorderWidth: 1.5,
            pointRadius: 6,
            pointHoverRadius: 9,
            pointHoverBackgroundColor: pointColors,
            pointHoverBorderColor: "#fff",
            pointHoverBorderWidth: 2,
            tension: 0.38,
            fill: true,
            backgroundColor: "rgba(122, 162, 247, 0.1)", // gradient static
        }]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { 
                display: true,
                position: "top",
                labels: {
                    color: "#c0caf5",
                    font: { size: 11 }
                }
            },
            tooltip: {
                backgroundColor: "#0d0f18",
                titleColor: "#7aa2f7",
                titleFont: { size: 11, weight: "bold" },
                bodyColor: "#c0caf5",
                bodyFont: { size: 12 },
                borderColor: "#1f2335",
                borderWidth: 1,
                padding: 10,
                displayColors: false,
                cornerRadius: 6,
                callbacks: {
                    label: (ctx) => {
                        const item = chartData[ctx.dataIndex];
                        return `Scor Risc: ${ctx.parsed.y}% — ${item?.category || "N/A"}`;
                    }
                }
            }
        },
        scales: {
            y: {
                min: 0,
                max: 100,
                title: {
                    display: true,
                    text: "Scor Risc (%)",
                    color: "#565f89",
                    font: { size: 10 }
                },
                ticks: {
                    color: "#565f89",
                    font: { size: 10 },
                    stepSize: 20,
                    callback: (v) => v + "%"
                },
                grid: {
                    color: (context) => {
                        if (context.tick.value === 80) return "rgba(247, 118, 142, 0.3)";
                        if (context.tick.value === 55) return "rgba(255, 159, 67, 0.2)";
                        return "rgba(34, 40, 49, 0.5)";
                    }
                }
            },
            x: {
                ticks: {
                    color: "#565f89",
                    font: { size: 9 },
                    maxRotation: 45,
                    minRotation: 45
                },
                grid: {
                    color: "rgba(34, 40, 49, 0.3)",
                    display: false
                }
            }
        }
    };

    console.log("Chart rendering with data:", { labels, scores }); // Debug

    return (
        <div className="chartPanel" style={{ minHeight: "400px", width: "100%" }}>
            <div className="chartPanelHeader">
                <span>Istoricul Dinamicii Emoționale</span>
                <div className="chartLegend">
                    <span className="legendDot critical"></span><span>Urgență (80-100%)</span>
                    <span className="legendDot high"></span><span>Risc Ridicat (55-79%)</span>
                    <span className="legendDot mid"></span><span>Stres (30-54%)</span>
                    <span className="legendDot low"></span><span>Neutru (0-29%)</span>
                </div>
            </div>
            <div className="chartWrapper" style={{ height: "350px", width: "100%" }}>
                <Line data={config} options={chartOptions} />
            </div>
        </div>
    );
}