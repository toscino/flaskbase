/**
 * Small helpers for flask-base apps (session auth — no waitForAuth).
 * Load: <script src="/static/flask_base/js/flask_base.js"></script>
 */
(function (global) {
    'use strict';

    function escapeHtml(text) {
        const el = document.createElement('div');
        el.textContent = text == null ? '' : String(text);
        return el.innerHTML;
    }

    async function apiFetch(url, options) {
        const opts = Object.assign(
            { headers: { 'Content-Type': 'application/json' } },
            options || {}
        );
        if (opts.body && typeof opts.body !== 'string') {
            opts.body = JSON.stringify(opts.body);
        }
        const res = await fetch(url, opts);
        let data = null;
        const ct = res.headers.get('content-type') || '';
        if (ct.indexOf('application/json') !== -1) {
            data = await res.json();
        }
        if (!res.ok) {
            const msg = (data && data.error) ? data.error : res.statusText;
            throw new Error(msg || 'Request failed');
        }
        return data;
    }

    function showMessage(element, message, type) {
        if (!element) return;
        element.textContent = message;
        element.style.display = message ? 'block' : 'none';
        element.classList.remove('success', 'error', 'success-message', 'error-message', 'message');
        if (!message) return;
        if (type === 'success') {
            element.classList.add('success-message');
        } else {
            element.classList.add('error-message');
        }
    }

    /**
     * Touch/mouse swipe on list rows. Swipe right reveals .swipe-pin; left reveals .swipe-delete.
     * options.onPin(itemEl, itemId), options.onDelete(itemEl, itemId) — return promises.
     */
    function initSwipeList(listEl, options) {
        if (!listEl) return;

        const itemSelector = (options && options.itemSelector) || '.swipe-item';
        const thresholdShow = (options && options.thresholdShow) || 70;
        const thresholdActivate = (options && options.thresholdActivate) || 80;
        const maxSwipe = (options && options.maxSwipe) || 100;

        let startX = 0;
        let currentX = 0;
        let isDragging = false;
        let currentItem = null;

        function getClientX(event) {
            if (event.touches && event.touches.length) return event.touches[0].clientX;
            if (event.changedTouches && event.changedTouches.length) {
                return event.changedTouches[0].clientX;
            }
            return event.clientX;
        }

        function startDrag(event) {
            if (event.target.closest('.swipe-confirm-btn')) return;
            const item = event.target.closest(itemSelector);
            if (!item) return;

            startX = getClientX(event);
            currentX = startX;
            isDragging = true;
            currentItem = item;
            const content = item.querySelector('.swipe-item-content');
            if (content) content.style.transition = 'none';
            item.style.cursor = 'grabbing';
        }

        function updateDrag(event) {
            if (!isDragging || !currentItem) return;
            currentX = getClientX(event);
            const deltaX = currentX - startX;
            const absDeltaX = Math.abs(deltaX);
            const content = currentItem.querySelector('.swipe-item-content');
            const pinLayer = currentItem.querySelector('.swipe-confirmation:not(.abandon)');
            const deleteLayer = currentItem.querySelector('.swipe-confirmation.abandon');

            if (!content) return;

            if (deltaX > 0) {
                const swipeDistance = Math.min(deltaX, maxSwipe);
                content.style.transform = 'translateX(' + swipeDistance + 'px)';
                if (deleteLayer) deleteLayer.classList.remove('show');
                if (pinLayer) {
                    if (swipeDistance > thresholdShow) pinLayer.classList.add('show');
                    else pinLayer.classList.remove('show');
                }
            } else if (deltaX < 0) {
                const swipeDistance = Math.max(deltaX, -maxSwipe);
                content.style.transform = 'translateX(' + swipeDistance + 'px)';
                if (pinLayer) pinLayer.classList.remove('show');
                if (deleteLayer) {
                    if (absDeltaX > thresholdShow) deleteLayer.classList.add('show');
                    else deleteLayer.classList.remove('show');
                }
            }
        }

        function endDrag() {
            if (!isDragging || !currentItem) return;

            const deltaX = currentX - startX;
            const absDeltaX = Math.abs(deltaX);
            const content = currentItem.querySelector('.swipe-item-content');
            const pinLayer = currentItem.querySelector('.swipe-confirmation:not(.abandon)');
            const deleteLayer = currentItem.querySelector('.swipe-confirmation.abandon');

            if (absDeltaX < thresholdActivate && content) {
                content.style.transition = 'transform 0.3s ease';
                content.style.transform = 'translateX(0)';
                if (pinLayer) pinLayer.classList.remove('show');
                if (deleteLayer) deleteLayer.classList.remove('show');
            }

            currentItem.style.cursor = '';
            isDragging = false;
            currentItem = null;
        }

        listEl.addEventListener('touchstart', startDrag, { passive: true });
        listEl.addEventListener('touchmove', updateDrag, { passive: true });
        listEl.addEventListener('touchend', endDrag);
        listEl.addEventListener('mousedown', function (event) {
            if (event.target.closest('.complete-confirm-btn, .abandon-confirm-btn, .swipe-confirm-btn')) {
                return;
            }
            startDrag(event);
            if (isDragging) event.preventDefault();
        });
        listEl.addEventListener('mousemove', updateDrag);
        listEl.addEventListener('mouseup', endDrag);
        listEl.addEventListener('mouseleave', endDrag);
        listEl.addEventListener('dragstart', function (event) {
            event.preventDefault();
        });

        document.addEventListener('mouseup', endDrag);

        listEl.addEventListener('click', async function (event) {
            const pinBtn = event.target.closest('.complete-confirm-btn, .swipe-confirm-btn.pin');
            const deleteBtn = event.target.closest('.abandon-confirm-btn, .swipe-confirm-btn.delete');
            if (!pinBtn && !deleteBtn) return;

            const item = event.target.closest(itemSelector);
            if (!item) return;
            const itemId = item.dataset.itemId;
            if (!itemId) return;

            const pinLayer = item.querySelector('.swipe-confirmation.swipe-pin');
            const deleteLayer = item.querySelector('.swipe-confirmation.swipe-delete');
            const content = item.querySelector('.swipe-item-content');

            if (pinBtn && options && options.onPin) {
                if (pinLayer) pinLayer.classList.remove('show');
                try {
                    await options.onPin(item, itemId);
                } catch (err) {
                    if (content) {
                        content.style.transition = 'transform 0.3s ease';
                        content.style.transform = 'translateX(0)';
                    }
                    throw err;
                }
            }

            if (deleteBtn && options && options.onDelete) {
                if (deleteLayer) deleteLayer.classList.remove('show');
                item.style.opacity = '0';
                item.style.transform = 'translateX(-20px)';
                try {
                    await options.onDelete(item, itemId);
                    setTimeout(function () {
                        item.remove();
                    }, 400);
                } catch (err) {
                    item.style.opacity = '';
                    item.style.transform = '';
                    if (content) {
                        content.style.transition = 'transform 0.3s ease';
                        content.style.transform = 'translateX(0)';
                    }
                    throw err;
                }
            }
        });
    }

    global.FlaskBase = {
        escapeHtml: escapeHtml,
        apiFetch: apiFetch,
        showMessage: showMessage,
        initSwipeList: initSwipeList,
    };
})(typeof window !== 'undefined' ? window : global);
