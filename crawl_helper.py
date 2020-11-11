from automation import CommandSequence, TaskManager

def run_crawl(sites, data_log_dir, blockers = None, headless = False, num_browsers = 1,
    http_instrument = False, cookie_instrument = False, navigation_instrument = False,
    js_instrument = False, callstack_instrument = False, sleep = 0, user_delay = None):
    '''
    Run a crawl over given sites, with given number of browsers.
    Save data and logs in given directory.
    '''

    # Load default manager params, and NUM_BROWSERS copies of default browser params
    manager_params, browser_params = TaskManager.load_default_params(num_browsers)

    # Update browser config
    for i in range(num_browsers):
        # Record HTTP Requests and Responses
        browser_params[i]['http_instrument'] = http_instrument
        # Record cookie changes
        browser_params[i]['cookie_instrument'] = cookie_instrument
        # Record Navigations
        browser_params[i]['navigation_instrument'] = navigation_instrument
        # Record JS Web API calls
        browser_params[i]['js_instrument'] = js_instrument
        # Record the callstack of all WebRequests made
        browser_params[i]['callstack_instrument'] = callstack_instrument
        # Activate given ad blocker
        if blockers is not None:
            for b in blockers:
                browser_params[i][b] = True
        # Set headless parameter
        if headless:
            browser_params[i]['display_mode'] = 'headless'

    # Update data and log directories
    manager_params['data_directory'] = data_log_dir
    manager_params['log_directory'] = data_log_dir
    manager_params['source_dump_path'] = data_log_dir

    # Instantiates the measurement platform
    # Commands time out by default after 60 seconds
    manager = TaskManager.TaskManager(manager_params, browser_params)

    # Visits the sites
    for site in sites:

        # Parallelize sites over all number of browsers set above.
        command_sequence = CommandSequence.CommandSequence(
            site, reset=True,
            callback=lambda success, val=site:
            print("CommandSequence {} done".format(val)))

        # Give the user some time to change settings
        if user_delay is not None:
            command_sequence.delay(delay_s = user_delay)

        # Then visit the page
        command_sequence.get(sleep=sleep, timeout=60)

        # Run commands across the three browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)

    # Shuts down the browsers and waits for the data to finish logging
    manager.close()