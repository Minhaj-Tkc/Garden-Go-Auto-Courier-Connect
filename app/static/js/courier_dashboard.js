document.addEventListener('DOMContentLoaded', () => {
    // Search Functionality
    document.getElementById('searchInput').addEventListener('input', function () {
      const searchValue = this.value.toLowerCase();
      const rows = document.querySelectorAll('#ordersTable tr');
  
      rows.forEach(row => {
        const name = row.cells[1]?.innerText.toLowerCase() || '';
        const orderId = row.cells[0]?.innerText.toLowerCase() || '';
        const address = row.cells[2]?.innerText.toLowerCase() || '';
  
        row.style.display = orderId.includes(searchValue) || address.includes(searchValue) || name.includes(searchValue) ? '' : 'none';
      });
    });
  
    // Filter Functionality
    document.getElementById('orderStatusFilter').addEventListener('change', function () {
      const filterValue = this.value;
      const rows = document.querySelectorAll('#ordersTable tr');
  
      rows.forEach(row => {
        const status = row.getAttribute('data-status');
        row.style.display = !filterValue || status === filterValue ? '' : 'none';
      });
    });
  
    // Update Status Functionality
    document.querySelectorAll('.update-status-btn').forEach(button => {
      button.addEventListener('click', function () {
        const orderId = this.getAttribute('data-order-id');
        const statusSelect = document.querySelector(`select[data-order-id='${orderId}']`);
        const newStatus = statusSelect.value;
  
        this.disabled = true;
        this.textContent = 'Updating...';
  
        fetch(`/update_status/${orderId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus }),
        })
          .then(response => {
            this.disabled = false;
            this.textContent = 'Update';
  
            if (response.ok) {
              toastr.success('Order status updated successfully!');
              // Reload the page after a successful update
              setTimeout(() => {
                window.location.reload();
              }, 2000); // Optional delay for user feedback
            } else {
              toastr.error('Failed to update order status.');
            }
          })
          .catch(() => {
            this.disabled = false;
            this.textContent = 'Update';
            toastr.error('An error occurred.');
          });
      });
    });
  });
  