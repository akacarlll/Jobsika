document.getElementById("gotoJobEngine").addEventListener("click", function() {
    const url = this.dataset.url; // read data-url attribute
    window.location.href = url;
});

// Function to render Plotly dashboards
function renderPlotlyDashboard(containerId, figure) {
    const container = document.getElementById(containerId);

    if (!container) {
        console.warn(`Container not found: ${containerId}`);
        return;
    }

    if (!figure) {
        container.innerHTML = `<div class="chart-error">
            <i class="fas fa-chart-line"></i>
            <span>Aucune donnée disponible</span>
        </div>`;
        return;
    }

    try {
        // Clear container
        container.innerHTML = '';

        // Get actual container dimensions from CSS
        const containerHeight = container.offsetHeight || 400;
        const containerWidth = container.offsetWidth || 600;

        // Plotly configuration
        const config = {
            responsive: true,
            displayModeBar: false,
            displaylogo: false
        };

        // Layout - use container dimensions
        const layout = {
            ...figure.layout,
            autosize: true,
            height: containerHeight,
            width: containerWidth,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: {
                l: 50,
                r: 50,
                t: 50,
                b: 50
            }
        };

        // Special handling for map - maximize space
        if (containerId === 'mapDashboard') {
            layout.margin = { l: 10, r: 10, t: 30, b: 10 };
        }

        Plotly.newPlot(container, figure.data, layout, config);

    } catch (error) {
        console.error(`Error rendering ${containerId}:`, error);
        container.innerHTML = `<div class="chart-error chart-error-critical">
            <i class="fas fa-exclamation-triangle"></i>
            <span>Erreur de chargement</span>
        </div>`;
    }
}

// Refresh function
document.getElementById('refreshBtn').addEventListener('click', function() {
    const btn = this;
    const icon = btn.querySelector('i');

    // Loading animation
    icon.classList.add('fa-spin');
    btn.disabled = true;
    btn.classList.add('opacity-50');

    // Simulate reload
    setTimeout(() => {
        window.location.reload();
    }, 1000);
});

// Initialization when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Correctly get the data from the script tag
    const dataElement = document.getElementById('dashboardsData');
    if (!dataElement) {
        console.error("The 'dashboardsData' script tag was not found.");
        return;
    }

    try {
        const dashboardsData = JSON.parse(dataElement.textContent);
        
        // This is the correct data access based on your provided log
        if (dashboardsData) {
            // The map and skills_pie are nested JSON strings, so they need to be parsed again
            if (dashboardsData.map) {
                renderPlotlyDashboard('mapDashboard', JSON.parse(dashboardsData.map), 500);
            }
            if (dashboardsData.skills_pie) {
                renderPlotlyDashboard('skillsPieDashboard', JSON.parse(dashboardsData.skills_pie));
            }
            // The timeline_dashboards are a nested object, access its properties directly
            if (dashboardsData.timeline_dashboards) {
                if (dashboardsData.timeline_dashboards.hourly) {
                    renderPlotlyDashboard('hourlyDashboard', JSON.parse(dashboardsData.timeline_dashboards.hourly));
                }
                if (dashboardsData.timeline_dashboards.daily) {
                    renderPlotlyDashboard('dailyDashboard', JSON.parse(dashboardsData.timeline_dashboards.daily));
                }
                if (dashboardsData.timeline_dashboards.timeline) {
                    renderPlotlyDashboard('timelineDashboard', JSON.parse(dashboardsData.timeline_dashboards.timeline));
                }
                if (dashboardsData.timeline_dashboards.cumulative) {
                    renderPlotlyDashboard('cumulativeDashboard', JSON.parse(dashboardsData.timeline_dashboards.cumulative));
                }
            }
        } else {
            console.error("No data found in 'dashboardsData' script tag.");
        }
    } catch (error) {
        console.error("Failed to parse JSON data from 'dashboardsData' script tag.", error);
    }

    // Progressive fade-in animation
    const cards = document.querySelectorAll('.fade-in');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
});

// Responsive handling for Plotly
window.addEventListener('resize', function() {
    clearTimeout(window.resizeTimer);
    window.resizeTimer = setTimeout(() => {
        const plotlyDivs = document.querySelectorAll('[id$="Dashboard"]');
        plotlyDivs.forEach(div => {
            if (div.data && div.layout) {
                // Get new container dimensions
                const newHeight = div.offsetHeight;
                const newWidth = div.offsetWidth;
                
                // Update layout with new dimensions
                Plotly.relayout(div, {
                    height: newHeight,
                    width: newWidth
                });
            }
        });
    }, 100);
});