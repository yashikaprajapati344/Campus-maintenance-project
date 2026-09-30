// Sample Initial Dataset
let tickets = [
    { id: "CMP048", student: "Rahul", dept: "B.Tech IT", building: "Computer Lab", room: "302", category: "IT", priority: "High", status: "Pending", date: "2026-08-18", cost: 0 },
    { id: "CMP035", student: "Rahul Singh", dept: "MCA", building: "Library", room: "311", category: "Internet", priority: "Medium", status: "In Progress", date: "2026-04-23", cost: 500 },
    { id: "CMP010", student: "Divya Mehta", dept: "BCA", building: "Block B", room: "126", category: "Electrical", priority: "Low", status: "Resolved", date: "2026-07-27", cost: 1112 }
];

let categoryChartInstance = null;
let statusChartInstance = null;

// View Navigation Switcher
function switchView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
    
    document.getElementById(`view-${viewName}`).classList.add('active');
    document.getElementById(`nav-${viewName}`)?.classList.add('active');

    updateUI();
}

// Add Complaint Logic
function handleFormSubmit(e) {
    e.preventDefault();
    const count = tickets.length + 1;
    const newTicket = {
        id: `CMP0${count < 100 ? (count < 10 ? '0' + count : count) : count}`,
        student: document.getElementById('studentName').value,
        dept: document.getElementById('department').value,
        building: document.getElementById('building').value,
        room: document.getElementById('roomNo').value,
        category: document.getElementById('category').value,
        priority: document.getElementById('priority').value,
        problem: document.getElementById('problem').value,
        status: 'Pending',
        date: new Date().toISOString().split('T')[0],
        cost: 0
    };

    tickets.unshift(newTicket);
    alert(`Complaint Registered Successfully!\nTicket ID: ${newTicket.id}`);
    document.getElementById('complaintForm').reset();
    switchView('tickets');
}

// Render UI Elements & Stats
function updateUI() {
    renderTicketLists();
    calculateMetrics();
    renderCharts();
}

function renderTicketLists() {
    const recentContainer = document.getElementById('recent-tickets-list');
    const allContainer = document.getElementById('all-tickets-list');
    
    const createCardHTML = (t) => `
        <div class="ticket-card">
            <div class="ticket-info">
                <h4><strong>${t.id}</strong> - ${t.student}</h4>
                <p>${t.building} • Rm ${t.room} • ${t.category}</p>
            </div>
            <div>
                <span class="badge ${t.status.toLowerCase().replace(' ', '-')}">${t.status}</span>
                <span class="date-text">${t.date}</span>
            </div>
        </div>
    `;

    recentContainer.innerHTML = tickets.slice(0, 5).map(createCardHTML).join('');
    allContainer.innerHTML = tickets.map(createCardHTML).join('');
}

function calculateMetrics() {
    const total = tickets.length;
    const resolved = tickets.filter(t => t.status === 'Resolved').length;
    const pending = tickets.filter(t => t.status === 'Pending').length;
    const progress = tickets.filter(t => t.status === 'In Progress').length;
    
    const totalCost = tickets.reduce((acc, t) => acc + t.cost, 0);
    const avgCost = resolved > 0 ? Math.round(totalCost / resolved) : 0;

    document.getElementById('dash-total').innerText = total;
    document.getElementById('dash-resolved').innerText = resolved;
    document.getElementById('dash-cost').innerText = `₹${avgCost}`;

    document.getElementById('rep-total').innerText = total;
    document.getElementById('rep-pending').innerText = pending;
    document.getElementById('rep-progress').innerText = progress;
    document.getElementById('rep-resolved').innerText = resolved;
}

function renderCharts() {
    const categories = ['Electrical', 'Furniture', 'Plumbing', 'IT', 'Internet', 'Cleaning'];
    const catCounts = categories.map(c => tickets.filter(t => t.category === c).length);

    const pending = tickets.filter(t => t.status === 'Pending').length;
    const progress = tickets.filter(t => t.status === 'In Progress').length;
    const resolved = tickets.filter(t => t.status === 'Resolved').length;

    // Category Bar Chart
    if(categoryChartInstance) categoryChartInstance.destroy();
    const ctxCat = document.getElementById('categoryChart').getContext('2d');
    categoryChartInstance = new Chart(ctxCat, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [{ label: 'Tickets', data: catCounts, backgroundColor: '#38bdf8' }]
        },
        options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
    });

    // Status Pie Chart
    if(statusChartInstance) statusChartInstance.destroy();
    const ctxStat = document.getElementById('statusChart').getContext('2d');
    statusChartInstance = new Chart(ctxStat, {
        type: 'pie',
        data: {
            labels: ['Pending', 'In Progress', 'Resolved'],
            datasets: [{ data: [pending, progress, resolved], backgroundColor: ['#f97316', '#38bdf8', '#22c55e'] }]
        }
    });
}

// CSV Export Helper
function exportCSV() {
    let csvContent = "data:text/csv;charset=utf-8,ID,Student,Building,Room,Category,Status,Date\n";
    tickets.forEach(t => {
        csvContent += `${t.id},${t.student},${t.building},${t.room},${t.category},${t.status},${t.date}\n`;
    });
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "complaints_report.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Initial Load
updateUI();