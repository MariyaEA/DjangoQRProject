// Utils

function DjangoTableUtils() {
    this.manager = false;
}


DjangoTableUtils.prototype.get_items = function(html_collection) {
    var items = [];
    for (var index=0; index < html_collection.length; index++) {
        items.push(html_collection.item(index));
    }
    return items;
}

DjangoTableUtils.prototype.on_document_ready = function(callback) {
    if (
        document.readyState === "complete" ||
        (document.readyState !== "loading" && !document.documentElement.doScroll)

    ) {
      callback();
    } else {
          document.addEventListener("DOMContentLoaded", callback);
    }
}

DjangoTableUtils.prototype.get_data = function(dom_element) {
    var data = {};
    var inputs = this.get_items(dom_element.querySelectorAll('input'));
    for (index in inputs) {
        var input = inputs[index];
        if (input.type == 'checkbox') {
            data[input.name] = input.checked;
        } else {
            data[input.name] = input.value;
        }
    }
    var selects = this.get_items(dom_element.querySelectorAll('select'));
    selects.forEach(function(select) {
        data[select.name] = select.value;
    });
    return data;
}

DjangoTableUtils.prototype.init = function() {
    var self = this;
    if (self.manager == false) {
        self.manager = new DjangoTableManager();
    }
}

DjangoTableUtils.prototype.serialize_data = function(data) {
    var serialized = '';
    for (key in data) {
        serialized += key + '=' + data[key] + "&";
    }
    return serialized;
}

DjangoTableUtils.prototype.replace_content = function(dom_element, new_content) {
    while(dom_element.firstChild) {
        dom_element.removeChild(dom_element.firstChild);
    }
    dom_element.appendChild(new_content);
}

DjangoTableUtils.prototype.generate_get_elem = function(dom_element, prefix) {
    var func = function get_elem(class_postfix) {
        return dom_element.querySelector('.' + prefix + '__' + class_postfix);
    };
    return func
}

// Manager

function DjangoTableManager() {
    this.tables = {};
    this.init_tables(document);
}

DjangoTableManager.prototype.init_tables = function(container) {
    var self = this;
    var tables = DTM.get_items(
        container.querySelectorAll('*[data-django_table="true"]')
    );
    for (index in tables) {
        var table = tables[index];
        if (!table.dataset.initalized) {
            self.tables[table.dataset.ident] = self.init_table(table);
            var event = new CustomEvent(
                'DTM:Manager:TableInitalized',
                {'id': table.dataset.ident}
            );
            document.dispatchEvent(event);
        }
    }
}

DjangoTableManager.prototype.init_table = function(table) {
    return new DjangoTable(table);
}

// Table

function DjangoTable(dom_element) {
    this.offset = 0;
    this.limit = 10;
    this.dom_element = dom_element;
    this.css_prefix = dom_element.dataset.css_prefix;
    this.ident = dom_element.dataset.ident;
    this.dom_element.dataset.initalized = true;
    this.urls = JSON.parse(this.dom_element.dataset.urls);
    this.get_elem = DTM.generate_get_elem(this.dom_element, this.css_prefix);
    this.register_buttons();
    this.register_events();
    this.sort_by = '';
    this.sort_dir = 'asc';
    this.get_data();
    this.counts_container = this.get_elem('counts');
    this.page_links = this.get_elem('nav__pages');
    this.item_name = this.counts_container.dataset.item_name;
    this.item_name_plural = this.counts_container.dataset.item_name_plural;
    this.modal = new DjangoTableModal(
        this, this.get_elem('modal')
    );
    this.active_action = null;
}


DjangoTable.prototype.get_data = function(page) {
    if (page === undefined) {
        page = 0;
    }
    var self = this;
    var data = this.get_request_args(page);
    var url = self.urls.data + "?" + DTM.serialize_data(data);
    fetch(url, {method: 'get'}).then(response => {
        if (!response.ok) {
            throw new Error('Bad response: ' + response.status)
        }
        return response.json()
    }).then(data => {
        self.draw_rows(data.rows);
        self.offset = (data.page - 1) * self.limit;
        self.update_counts(data.total, data.filtered);
        self.update_prev_and_next(data.page, data.pages);
        self.generate_pagelinks(data.page, data.pages);
    }).catch(error => console.log(error));
}


DjangoTable.prototype.draw_rows = function(rows) {
    // remove old rows
    var tbody = this.dom_element.querySelector('tbody');
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    if (rows.length == 0) {
        var row_container = document.createElement("tr");
        var column_container = document.createElement("td");
        var text = document.createTextNode('cannot find any data');
        column_container.appendChild(text);
        var number_of_columns = this.get_elem('table__head tr')
            .querySelectorAll('th').length;
        column_container.colSpan = number_of_columns;
        column_container.style.textAlign = 'center';
        row_container.appendChild(column_container);
        tbody.appendChild(row_container);
    }
    // create and append new rows
    for (var index in rows) {
        var row = rows[index];
        var row_container = document.createElement("tr");
        for (var index2 in row) {
            var cell = row[index2];
            var cell_container = document.createElement("td");
            cell_container.innerHTML = cell;
            row_container.appendChild(cell_container);
        }
        tbody.appendChild(row_container);
    }
}

DjangoTable.prototype.item_name_with_count = function(count) {
    if (count === 1) {
        return "1 " + this.item_name;
    }
    return count + " " + this.item_name_plural;
}

DjangoTable.prototype.update_counts = function(total, filtered) {
    var to_show = Math.min(this.limit, filtered);
    var first = this.offset + 1;
    var last = Math.min(this.offset + this.limit, filtered);
    var range = "1";
    if (first != last)
        range = " " + first + " - " + last;
    var text = "Showing " + range + " of " + this.item_name_with_count(filtered);
    if (total != filtered)
        text += " (filtered from " + this.item_name_with_count(total) + " in total)"
    var textNode = document.createTextNode(text);
    DTM.replace_content(this.counts_container, textNode);
}

DjangoTable.prototype.update_prev_and_next = function(page, pages) {
    if (page > 1) {
        this.previous_button.removeAttribute("disabled");
    } else {
        this.previous_button.setAttribute("disabled", true);
    }
    if (pages > page) {
        this.next_button.removeAttribute("disabled");
    } else {
        this.next_button.setAttribute("disabled", true);
    }
}

DjangoTable.prototype.generate_pagelinks = function(page, pages) {
    var self = this;
    while(this.page_links.firstChild) {
        this.page_links.removeChild(this.page_links.firstChild)
    }
    if (pages < 8) {
        for (var cnt=1; cnt<=pages; cnt++) {
            self.add_pagelink(cnt, cnt==page);
        }
    } else if (page < 5) {
        for (var cnt=1; cnt<6; cnt++) {
            self.add_pagelink(cnt, cnt==page);
        }
        self.add_pagespacer();
        self.add_pagelink(pages, false);
    } else if (page > pages - 4) {
        self.add_pagelink(1, false);
        self.add_pagespacer();
        for (var cnt=pages-4; cnt<=pages; cnt++) {
            self.add_pagelink(cnt, cnt==page);
        }
    } else {
        self.add_pagelink(1, false);
        self.add_pagespacer();
        self.add_pagelink(page - 1, false);
        self.add_pagelink(page, true);
        self.add_pagelink(page + 1, false);
        self.add_pagespacer();
        self.add_pagelink(pages, false);
    }
}

DjangoTable.prototype.add_pagelink = function(page_number, is_active) {
    var self = this;
    var number = document.createTextNode(page_number);
    var link = document.createElement('a');
    link.classList.add(this.css_prefix + '__nav__page');
    if (is_active) {
        link.classList.add(this.css_prefix + "__nav__page--active");
    }
    link.appendChild(number);
    this.page_links.appendChild(link);
    link.addEventListener('click', function() {self.get_data(page_number);});
}

DjangoTable.prototype.add_pagespacer = function() {
    var spacer = document.createTextNode('..');
    this.page_links.appendChild(spacer);
}

DjangoTable.prototype.get_request_args = function(page) {
    var args = {
        'limit': this.limit,
        'offset': this.offset,
        'page': page,
        'sort_by': this.sort_by,
        'sort_dir': this.sort_dir
    };
    var filters = DTM.get_items(this.dom_element.querySelectorAll('.' + this.css_prefix + '__filter'));
    for (index in filters) {
        var filter = filters[index];
        var name = filter.dataset.name;
        args[name] = JSON.stringify(DTM.get_data(filter));
    }
    return args;
}


DjangoTable.prototype.register_buttons = function() {
    var self = this;
    this.refresh_button = this.dom_element.querySelector('.' + this.css_prefix + '__nav__refresh');
    this.refresh_button.addEventListener('click', function() {self.get_data();});
    this.previous_button = this.dom_element.querySelector('.' + this.css_prefix + '__nav__previous');
    this.previous_button.addEventListener('click', function() {
        self.offset = Math.max(0, self.offset - self.limit);
        self.get_data();
    });
    this.next_button = this.dom_element.querySelector('.' + this.css_prefix + '__nav__next');
    this.next_button.addEventListener('click', function() {
        self.offset += self.limit;
        self.get_data();
    });
    window.addEventListener('resize', function() {
        var menu_class = self.css_prefix + '__action__menu';
        self.dom_element.querySelectorAll('.' + menu_class).forEach(e => {
            e.classList.remove(menu_class + '--active');
            e.style.top = 0;
            e.style.left = 0;
        });
    });
    this.get_elem('table__body').addEventListener(
        'click',
        function(event) {
            var action_class = self.css_prefix + '__action__';
            if (event.target.classList.contains(action_class + 'button')) {
                event.stopPropagation();
                self.close_action_menus()
                var action = event.target.parentElement;
                var menu = action.querySelector('.' + action_class + 'menu');
                var pos = action.getBoundingClientRect();
                menu.style.top = (pos.top + pageYOffset + 20) + 'px';
                menu.style.left = (pos.left + pageXOffset - menu.offsetWidth + 115) + 'px';
                menu.classList.add(action_class + 'menu--active');
            } else if (event.target.classList.contains(action_class + 'menu__item')) {
                self.open_action(event.target);
            }

        }
    );
    document.addEventListener('click', function(event){
        if (event.button != 2) {
            self.close_action_menus();
        };
    });
}

DjangoTable.prototype.close_action_menus = function() {
    var active_class = this.css_prefix + '__action__menu--active';
    var open_menus = document.querySelectorAll('.' + active_class);
    open_menus.forEach(function(menu) {menu.classList.remove(active_class)})
}

DjangoTable.prototype.register_events = function() {
    var self = this;
    var filters = this.dom_element.querySelector('.' + this.css_prefix + '__filters');
    filters.addEventListener('keypress', function(event){
        if (event.keyCode === 13) {
            self.get_data(1);
            event.preventDefault();
        }
    });
    var selects = filters.querySelectorAll('select');
    selects.forEach(function(select) {
        select.addEventListener('change', function(event){
            self.get_data(1);
        });
    });
    var form = filters.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            window.history.back();
        }, true);
    }
    date_filter = DTM.get_items(filters.querySelectorAll('input[type="date"]'));
    for (index in date_filter) {
        date_filter[index].onchange = function(e) {self.get_data(1);}
    }
    checkbox_filter = DTM.get_items(filters.querySelectorAll('input[type="checkbox"]'));
    for (index in checkbox_filter) {
        checkbox_filter[index].onchange = function(e) {self.get_data(1);}
    }
    var limit_selector = self.dom_element.querySelector('.' + this.css_prefix + '__limit__selector');
    limit_selector.addEventListener('change', function(){
        var options = DTM.get_items(limit_selector.querySelectorAll('option'));
        for (var index in options) {
            var option = options[index];
            if (option.selected) {
                self.limit = Number(option.value);
                self.get_data(1);
                break;
            }
        }
    });
    var sortable_columns = DTM.get_items(
        self.dom_element.querySelectorAll('.' + self.css_prefix + '__column--sortable')
    );
    for (var index in sortable_columns) {
        var column = sortable_columns[index];
        column.addEventListener('click', function(event){
            self.sort_by_column(event.target);
        });
    }
    self.get_elem('table__body').addEventListener('contextmenu', function(event) {
        var row = event.target.closest('tr');
        var menu = row.querySelector('.' + self.css_prefix + '__action__menu');
        if (menu) {
            event.preventDefault();
            self.close_action_menus();
            menu.style.left = (event.clientX + pageXOffset) + 'px';
            menu.style.top = (event.clientY + pageYOffset) + 'px';
            menu.classList.add(self.css_prefix + '__action__menu--active');
        }
    });
}

DjangoTable.prototype.open_action = function(action_item){
    var self = this;
    var row = action_item.closest('tr');
    row.classList.add(this.css_prefix + '__row--active_action');
    var action = action_item.closest('.' + this.css_prefix + '__action');
    var action_id = action_item.dataset.ident;
    action_name = action_item.innerHTML;
    var pks = JSON.stringify([Number(action.dataset.item_pk)]);
    var content = document.createElement('span');
    var spinner = document.createElement('span');
    var text = document.createTextNode(
        'Fetching Action "' + action_name + '" for ' + this.item_name + ' with id ' + pks,
    );
    spinner.classList.add(this.css_prefix + "__spinner");
    content.appendChild(spinner);
    content.append(text);
    this.modal.current_action = action_item;
    this.modal.show_message(
        content,
        action_name
    );
    var url = self.urls.action + "?" + DTM.serialize_data({'ids': pks, 'action_id': action_id});
    fetch(url, {method: 'get'}).then(function(response) {
        if (!response.ok) {
            throw new Error('Bad response: ' + response.status)
        }
        return response.text()
    }).then(function(response) {
        data = JSON.parse(response);
        self.render_action(data, action_id, pks);
    }).catch(err => console.log(err));
}

DjangoTable.prototype.render_action = function(data, action_id, pks) {
    var form = document.createElement('form');
    form.innerHTML = data.content;
    this.modal.set_body(form);
    this.modal.set_footer('');
    this.modal.set_title(data.title);
    if (data.redirect_url) {
        this.modal.add_button(data.submit_button, () => {
            window.location=data.redirect_url;
        });
        this.modal.add_button(data.abort_button, () => {
            this.modal.close();
        }, 'secondary');
        return
    }
    if (!data.only_get) {
        this.modal.add_button(data.submit_button, () => this.submit_action(action_id, pks));
    }
    if (data.abort_button) {
        this.modal.add_button(data.abort_button, () => this.modal.close(), 'secondary');
    }
}

DjangoTable.prototype.submit_action = function(action_id, pks) {
    var self = this;
    var form = this.modal.dom_element.querySelector('form');
    var form_data = new FormData(form);
    form_data.append('ids', pks);
    form_data.append('action_id', action_id);
    fetch(self.urls.action, {
        method: 'post',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        redirect: 'follow',
        referrer: 'no-referrer',
        body: form_data
    }).then(response => {
        if (!response.ok) {
            throw new Error('Bad Response: ' + response.status);
        }
        return response.text()
    }).then(data => {
        data = JSON.parse(data);
        if (data.redirect_url) {
            self.modal.close();
            window.location = data.redirect_url;
        } else if (data.content) {
            self.render_action(data, action_id, pks);
        } else {
            self.modal.close();
        }
        self.get_data();
    }).catch(error => self.modal.show_message(error));
}

DjangoTable.prototype.sort_by_column  = function(column){
    this.sort_by = column.dataset.title;
    var sortable_columns = DTM.get_items(
        this.dom_element.querySelectorAll('.' + this.css_prefix + '__column--sortable')
    );
    var desc = column.classList.contains('desc');
    if (!desc && !column.classList.contains('asc')) {
        // there was no ordering on this column before -> remove other orderings if exist
        for (var i in sortable_columns) {
            var c = sortable_columns[i];
            c.classList.remove('desc');
            c.classList.remove('asc');
        }
        // and now set to desc so its changed to asc as first entrypoint
        column.classList.add('desc');
        desc = true;
    }
    if (desc) {
        column.classList.replace('desc', 'asc');
        this.sort_dir = 'asc';
    } else {
        column.classList.replace('asc', 'desc');
        this.sort_dir = 'desc';
    }
    this.get_data(1);
}

function DjangoTableModal(table, dom_element) {
    var self = this;
    this.table = table
    this.css_prefix = table.css_prefix + '__modal';
    this.dom_element = dom_element;
    this.get_elem = DTM.generate_get_elem(this.dom_element, this.css_prefix);
    this.get_elem('close').addEventListener('click', function() {self.close()});
    this.current_action = null;
}

DjangoTableModal.prototype.show_message = function(message, title) {
    var self = this;
    this.set_body(message);
    if (title) {
        this.set_title(title);
    } else {
        this.set_title('');
    }
    this.set_footer('');
    this.add_button('Ok', function() {self.close()});
    this.open();
    this.register_events();
}

DjangoTableModal.prototype.__set_element = function(element, content) {
    var element = this.get_elem(element);
    while (element.firstChild) {
        element.removeChild(element.firstChild)
    }
    if (typeof content == 'string') {
        content = document.createTextNode(content);
    }
    element.appendChild(content);
}

DjangoTableModal.prototype.register_events = function() {
    this.dom_element.addEventListener('keypress', function(event){
        if (event.keyCode === 13) {
            event.preventDefault();
        }
    });
}

DjangoTableModal.prototype.add_button = function(button_name, callback, class_name) {
    var button = document.createElement('button');
    button.innerHTML = button_name;
    if (class_name) {
        button.classList.add(class_name);
    }
    button.addEventListener('click', callback);
    var footer = this.get_elem('footer');
    footer.appendChild(button);
    var ev = new Event('DTM:Modal:added_button', {bubbles: true});
    button.dispatchEvent(ev);
    return button;
}

DjangoTableModal.prototype.set_title = function(content) {
    this.__set_element('title', content);
}

DjangoTableModal.prototype.set_body = function(content) {
    this.__set_element('body', content);
}

DjangoTableModal.prototype.set_footer = function(content) {
    this.__set_element('footer', content);
}

DjangoTableModal.prototype.open = function() {
    this.dom_element.classList.add(this.css_prefix + '--open');
    if (this.get_elem('title').innerHTML) {
        this.get_elem('header').classList.add(this.css_prefix + '__header--border');
    } else {
        this.get_elem('header').classList.remove(this.css_prefix + '__header--border');
    }
    var ev = new Event('DTM:Modal:opened', {bubbles: true});
    this.dom_element.dispatchEvent(ev);
}

DjangoTableModal.prototype.close = function() {
    this.dom_element.classList.remove(this.css_prefix + '--open');
    var ev = new Event('DTM:Modal:closed', {bubbles: true});
    this.dom_element.dispatchEvent(ev);
    if (this.current_action) {
        var row = this.current_action.closest('tr');
        row.classList.remove(
            this.table.css_prefix + '__row--active_action'
        );
        this.current_action = null;
    }
}


// Initalization
var DTM = new DjangoTableUtils();
DTM.on_document_ready(function(){DTM.init();});
