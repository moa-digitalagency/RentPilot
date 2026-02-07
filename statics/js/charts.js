
/*
* Nom de l'application : RentPilot
* Description : JavaScript logic for charts.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
*/
// Config Chart.js pour les dépenses

function initExpensesChart(canvasId, dataLabels, dataValues) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: dataLabels, // e.g., ['Loyer', 'Électricité', 'Internet', 'Eau']
            datasets: [{
                label: 'Répartition des charges',
                data: dataValues, // e.g., [500, 50, 30, 20]
                backgroundColor: [
                    'rgba(99, 102, 241, 0.8)', // Indigo
                    'rgba(16, 185, 129, 0.8)', // Emerald
                    'rgba(244, 63, 94, 0.8)',  // Rose
                    'rgba(251, 191, 36, 0.8)'  // Amber
                ],
                borderColor: [
                    'rgba(255, 255, 255, 1)',
                    'rgba(255, 255, 255, 1)',
                    'rgba(255, 255, 255, 1)',
                    'rgba(255, 255, 255, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            family: "'Inter', sans-serif"
                        }
                    }
                }
            },
            cutout: '70%', // Donut thickness
        }
    });
}