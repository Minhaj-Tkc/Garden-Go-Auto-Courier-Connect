// Filter orders in the table based on the search input
function searchOrders() {
    const searchInput = document.getElementById("orderSearch").value.toLowerCase();
    const table = document.getElementById("orderTable");
    const rows = table.getElementsByTagName("tr");
  
    for (let i = 1; i < rows.length; i++) {
      const cells = rows[i].getElementsByTagName("td");
      let match = false;
  
      for (let j = 0; j < cells.length - 1; j++) {
        if (cells[j].innerText.toLowerCase().includes(searchInput)) {
          match = true;
          break;
        }
      }
  
      rows[i].style.display = match ? "" : "none";
    }
  }



  document.addEventListener('DOMContentLoaded', () => {
    const rows = document.querySelectorAll('.clickable-row');
  
    rows.forEach(row => {
      row.addEventListener('click', () => {
        const href = row.getAttribute('data-href');
        if (href) {
          window.location.href = href;
        }
      });
    });
  });
  
  