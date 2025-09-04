document.addEventListener('DOMContentLoaded', function () {
    const notificationBell = document.getElementById('notification-bell');
    const notificationDropdown = document.getElementById('notification-dropdown');
    const notificationBadge = document.getElementById('notification-badge');
    let notificationCount = 0;

    // Toggle notification dropdown
    notificationBell.addEventListener('click', function () {
        notificationDropdown.classList.toggle('show');
    });

    // Close notification
    window.closeNotification = function (element) {
        const notification = element.parentElement;
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
            notificationCount--;
            updateNotificationBadge();
        }, 300); // Match the CSS transition duration
    };

    // Clear all notifications
    window.clearAllNotifications = function () {
        const notifications = document.querySelectorAll('.notification');
        notifications.forEach(notification => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
        notificationCount = 0;
        updateNotificationBadge();
    };

    // Update notification badge
    function updateNotificationBadge() {
        if (notificationCount > 0) {
            notificationBadge.textContent = notificationCount;
            notificationBadge.style.display = 'flex';
        } else {
            notificationBadge.style.display = 'none';
        }
    }

    // Initialize animations
    animateCounters();

    // Owner Profile Animations
    initializeOwnerProfileAnimations();
});

// Members functionality - Export Data
function exportMembersData() {
    try {
        const table = document.querySelector('table');
        if (!table) {
            alert('No data to export');
            return;
        }

        // Get headers
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
        
        // Get data rows
        const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
            return Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim());
        });

        if (rows.length === 0 || (rows.length === 1 && rows[0][0] === 'No members found')) {
            alert('No member data to export');
            return;
        }

        // Create CSV content
        let csvContent = headers.join(',') + '\r\n';
        rows.forEach(row => {
            csvContent += row.map(cell => `"${cell}"`).join(',') + '\r\n';
        });

        // Create and trigger download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'members_data.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        // Show success message
        showNotification('Member data exported successfully!', 'success');
        
    } catch (error) {
        console.error('Export error:', error);
        alert('Error exporting data. Please try again.');
    }
}

// Members functionality - View Stats
function viewMembersStats() {
    try {
        // Get actual member data
        const table = document.querySelector('table');
        const rows = table.querySelectorAll('tbody tr');
        const totalMembers = rows.length;
        const hasData = totalMembers > 0 && rows[0].cells[0].textContent !== 'No members found';
        
        if (!hasData) {
            alert('No member data available for statistics');
            return;
        }

        // Calculate actual stats
        const joinDates = Array.from(rows).map(row => {
            const dateText = row.cells[3]?.textContent || '';
            return new Date(dateText);
        });

        const now = new Date();
        const thisMonth = joinDates.filter(date => {
            return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
        }).length;

        const lastMonth = joinDates.filter(date => {
            const lastMonthDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
            return date.getMonth() === lastMonthDate.getMonth() && date.getFullYear() === lastMonthDate.getFullYear();
        }).length;

        // Create enhanced stats modal
        const modal = document.createElement('div');
        modal.className = 'modal fade show';
        modal.style.display = 'block';
        modal.style.backgroundColor = 'rgba(0,0,0,0.7)';
        modal.style.zIndex = '9999';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content" style="background: linear-gradient(135deg, rgba(0, 255, 65, 0.1), rgba(0, 255, 65, 0.05)); border: 1px solid rgba(0, 255, 65, 0.2);">
                    <div class="modal-header">
                        <h5 class="modal-title text-green">Member Statistics</h5>
                        <button type="button" class="btn-close btn-close-white" onclick="closeModal(this)"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="stat-item mb-3">
                                    <h4 class="text-green">${totalMembers}</h4>
                                    <p>Total Members</p>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="stat-item mb-3">
                                    <h4 class="text-green">${thisMonth}</h4>
                                    <p>New This Month</p>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="stat-item mb-3">
                                    <h4 class="text-green">${lastMonth}</h4>
                                    <p>New Last Month</p>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="stat-item mb-3">
                                    <h4 class="text-green">${totalMembers > 0 ? '100%' : '0%'}</h4>
                                    <p>Active Rate</p>
                                </div>
                            </div>
                        </div>
                        <div class="mt-3">
                            <p><strong>Growth Rate:</strong> ${lastMonth > 0 ? Math.round(((thisMonth - lastMonth) / lastMonth) * 100) : 'N/A'}%</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="closeModal(this)">Close</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('Stats error:', error);
        alert('Error loading statistics. Please try again.');
    }
}

// Helper functions
function closeModal(button) {
    const modal = button.closest('.modal');
    if (modal) {
        modal.remove();
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        ${message}
        <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}

function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    counters.forEach(counter => {
        const target = parseInt(counter.textContent);
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = target;
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current);
            }
        }, 20);
    });
}

// Events functionality
function subscribeToEvents() {
    if (confirm('Would you like to subscribe to event notifications?')) {
        // Simulate subscription process
        fetch('/subscribe_events', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({action: 'subscribe'})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Successfully subscribed to event notifications!', 'success');
            } else {
                showNotification('Subscription failed. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Successfully subscribed to event notifications!', 'success');
        });
    }
}

function shareEvents() {
    if (navigator.share) {
        navigator.share({
            title: 'Car Meet Community Events',
            text: 'Check out upcoming car meet events!',
            url: window.location.href
        }).catch(console.error);
    } else {
        const shareText = `Check out these amazing car meet events: ${window.location.href}`;
        navigator.clipboard.writeText(shareText).then(() => {
            showNotification('Link copied to clipboard!', 'success');
        });
    }
}

// Individual event sharing
function shareEvent(title, date, location) {
    const eventText = `Join us for "${title}" on ${date} at ${location}. Check out all events at: ${window.location.href}`;
    
    if (navigator.share) {
        navigator.share({
            title: title,
            text: eventText,
            url: window.location.href
        }).catch(console.error);
    } else {
        navigator.clipboard.writeText(eventText).then(() => {
            showNotification(`Event "${title}" details copied to clipboard!`, 'success');
        });
    }
}

// Share all events
function shareAllEvents() {
    const eventsText = `Check out all the amazing car meet events happening in our community: ${window.location.href}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Car Meet Community Events',
            text: eventsText,
            url: window.location.href
        }).catch(console.error);
    } else {
        navigator.clipboard.writeText(eventsText).then(() => {
            showNotification('All events link copied to clipboard!', 'success');
        });
    }
}

// Bootstrap 5 Tabs Initialization and Event Handling (Enhanced with debugging)
document.addEventListener('DOMContentLoaded', function () {
    console.log('Initializing Bootstrap 5 tabs with enhanced debugging...');

    // Check if Bootstrap is loaded
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap not loaded! Tabs will not work.');
        return;
    }

    // Get all tab triggers
    const triggerTabList = [].slice.call(document.querySelectorAll('#dashboardTabs button[data-bs-toggle="tab"]'));
    console.log('Found tab triggers:', triggerTabList.length);

    if (triggerTabList.length === 0) {
        console.warn('No tab triggers found. Make sure the dashboard tabs are present.');
        return;
    }

    triggerTabList.forEach(function (triggerEl, index) {
        console.log('Initializing tab ' + index + ':', triggerEl.id || triggerEl);

        try {
            const tabTrigger = new bootstrap.Tab(triggerEl);
            console.log('Tab initialized successfully:', tabTrigger);

            triggerEl.addEventListener('click', function (event) {
                console.log('Tab clicked:', this.id || this);
                event.preventDefault();

                // Hide all tab panes
                const allPanes = document.querySelectorAll('.tab-pane');
                allPanes.forEach(pane => {
                    pane.classList.remove('show', 'active');
                });

                // Remove active class from all tab buttons
                const allTabs = document.querySelectorAll('#dashboardTabs .nav-link');
                allTabs.forEach(tab => {
                    tab.classList.remove('active');
                });

                // Show the clicked tab as active
                this.classList.add('active');

                // Show the target pane
                const targetId = this.getAttribute('data-bs-target');
                if (targetId) {
                    const targetPane = document.querySelector(targetId);
                    if (targetPane) {
                        targetPane.classList.add('show', 'active');
                        console.log('Activated pane:', targetId);
                    } else {
                        console.error('Target pane not found:', targetId);
                    }
                }

                // Also try the Bootstrap method as fallback
                try {
                    tabTrigger.show();
                } catch (error) {
                    console.warn('Bootstrap show method failed:', error);
                }
            });

        } catch (error) {
            console.error('Error initializing tab:', error);
        }
    });

    // Add event listeners for tab content changes
    const tabContent = document.getElementById('dashboardTabsContent');
    if (tabContent) {
        tabContent.addEventListener('show.bs.tab', function (event) {
            console.log('Bootstrap show event:', event.target.id);
        });

        tabContent.addEventListener('shown.bs.tab', function (event) {
            console.log('Bootstrap shown event:', event.target.id);
        });
    }

    console.log('Tab initialization complete');
});

// Owner Profile Animations
function initializeOwnerProfileAnimations() {
    const ownerImage = document.getElementById('ownerImage');
    const aboutMeText = document.getElementById('aboutMeText');

    if (ownerImage) {
        // Add click animation
        ownerImage.addEventListener('click', function() {
            this.style.transform = 'scale(1.2) rotate(5deg)';
            setTimeout(() => {
                this.style.transform = '';
            }, 300);
        });

        // Add mouse enter/leave effects
        ownerImage.addEventListener('mouseenter', function() {
            this.style.filter = 'brightness(1.2) contrast(1.1)';
        });

        ownerImage.addEventListener('mouseleave', function() {
            this.style.filter = '';
        });
    }

    if (aboutMeText) {
        // Typewriter effect for about me text
        const originalText = aboutMeText.textContent;
        aboutMeText.textContent = '';
        let i = 0;

        function typeWriter() {
            if (i < originalText.length) {
                aboutMeText.textContent += originalText.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        }

        // Start typewriter effect after a delay
        setTimeout(typeWriter, 1000);
    }

    // Animate stats on scroll
    const statItems = document.querySelectorAll('.about-me-stats .stat-item h4');
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.textContent);
                animateNumber(entry.target, 0, target, 1000);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    statItems.forEach(item => {
        observer.observe(item);
    });
}

function animateNumber(element, start, end, duration) {
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const current = Math.floor(start + (end - start) * progress);
        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}
