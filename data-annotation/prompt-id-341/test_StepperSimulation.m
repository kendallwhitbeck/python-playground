function test_StepperSimulation
% test_StepperSimulation      ------ Response C
% --------------------------------------------------------------
% This script systematically tests StepperSimulation.m by:
%   1) Defining multiple sets of input parameters for each type of input
%   2) Running the StepperSimulation script for each set of parameters
%   3) Extracting and storing the results for later checks
%
% ASSUMPTION: The user has the StepperSimulation.m script in the same folder
% or on the MATLAB path. StepperSimulation.m will be run “as-is,” meaning
% we rely on variable assignments in the base workspace and the switched
% input_type to define how it behaves.
%
% You can further expand the test coverage by adding more parameter sets.

    %% Housekeeping
    clearvars;  % Clear workspace
    close all;   % Close figures
    clc;

    %% Define Test Cases
    
    % Each test case is a struct with fields:
    %   'name'           - descriptive name of the test
    %   'input_type'     - which input type in StepperSimulation (e.g. 'step','ramp','sine','trajectory')
    %   'parameters'     - key parameters needed by the script for that input type
    %
    % Example combination:
    % test_cases(1).name = 'Step_input_speed_1_rev_s';
    % test_cases(1).input_type = 'step';
    % test_cases(1).parameters.target_speed = 1; % rev/s

    test_cases = [];
    idx = 1;  % Will increment for each test case

    % 1) Step Inputs with different speeds
    speeds = [0.5, 1.0, 2.0];
    for sp = speeds
        test_cases(idx).name = sprintf('Step_input_speed_%0.2f_rev_s', sp);
        test_cases(idx).input_type = 'step';
        test_cases(idx).parameters.target_speed = sp;
        idx = idx + 1;
    end

    % 2) Ramp Inputs with different ramp times and target speeds
    ramp_times = [1, 2];
    ramp_speeds = [1, 2];
    for rt = ramp_times
        for rs = ramp_speeds
            test_cases(idx).name = sprintf('Ramp_input_rampT_%0.2f_speed_%0.2f', rt, rs);
            test_cases(idx).input_type = 'ramp';
            test_cases(idx).parameters.ramp_time = rt;
            test_cases(idx).parameters.target_speed = rs;
            idx = idx + 1;
        end
    end

    % 3) Sinusoidal Inputs with different amplitudes/frequencies
    amplitudes = [0.5, 1.0];
    frequencies = [0.2, 0.5, 1.0];
    for a = amplitudes
        for f = frequencies
            test_cases(idx).name = sprintf('Sine_input_amp_%0.2f_freq_%0.2f', a, f);
            test_cases(idx).input_type = 'sine';
            test_cases(idx).parameters.amplitude = a;
            test_cases(idx).parameters.frequency = f;
            idx = idx + 1;
        end
    end

    % 4) Trajectory Inputs (arbitrary sets of waypoints)
    % You can add multiple trajectory sets to test the interpolation
    trajectory_sets = {
       struct('waypoints_time',[0 1 2 3 4],'waypoints_position',[0 0.5 1 0.5 0])
       struct('waypoints_time',[0 2 5],'waypoints_position',[0 1.5 1])  % Another example
    };
    for tInd = 1:length(trajectory_sets)
        test_cases(idx).name = sprintf('Trajectory_input_set_%d', tInd);
        test_cases(idx).input_type = 'trajectory';
        test_cases(idx).parameters.waypoints_time = trajectory_sets{tInd}.waypoints_time;
        test_cases(idx).parameters.waypoints_position = trajectory_sets{tInd}.waypoints_position;
        idx = idx + 1;
    end

    %% Run Each Test
    % Create a results struct array to store outcome data and plots

    testResults = struct( ...
        'TestName', [], ...
        'InputType', [], ...
        'Parameters', [], ...
        'TimeVector', [], ...
        'PositionVector', [], ...
        'VelocityVector', [], ...
        'Status', [] );

    for t = 1:length(test_cases)
        % Print to command window for tracking
        fprintf('\n\nRunning test %d of %d: %s\n', t, length(test_cases), test_cases(t).name);

        % Prepare test-specific parameters in the base workspace so
        % StepperSimulation.m can directly pick them up
        
        assignin('base','input_type',   test_cases(t).input_type);

        switch test_cases(t).input_type
            case 'step'
                assignin('base','target_speed', test_cases(t).parameters.target_speed);
            case 'ramp'
                assignin('base','ramp_time',    test_cases(t).parameters.ramp_time);
                assignin('base','target_speed', test_cases(t).parameters.target_speed);
            case 'sine'
                assignin('base','amplitude',    test_cases(t).parameters.amplitude);
                assignin('base','frequency',    test_cases(t).parameters.frequency);
            case 'trajectory'
                assignin('base','waypoints_time',     test_cases(t).parameters.waypoints_time);
                assignin('base','waypoints_position', test_cases(t).parameters.waypoints_position);
            otherwise
                error('Unknown input type: %s', test_cases(t).input_type);
        end

        % Optionally override default simulation parameters in StepperSimulation (like dt) if desired:
        % Example: assignin('base','dt',0.001);

        % Clear any leftover variables from previous runs inside the script
        evalin('base','clear pos_vector vel_vector t_vector');

        % Run the script
        try
            evalin('base','StepperSimulation');  % This executes StepperSimulation.m in the base workspace
            test_status = 'Passed';
        catch ME
            % If an error occurs, store it and skip capturing results
            test_status = sprintf('Failed: %s', ME.message);
        end

        % Attempt to retrieve the results from the base workspace
        if strcmp(test_status,'Passed')
            timeVec = evalin('base','t_vector');
            posVec  = evalin('base','pos_vector');
            velVec  = evalin('base','vel_vector');
        else
            timeVec = [];
            posVec  = [];
            velVec  = [];
        end

        % Store in testResults
        testResults(t).TestName        = test_cases(t).name;
        testResults(t).InputType       = test_cases(t).input_type;
        testResults(t).Parameters      = test_cases(t).parameters;
        testResults(t).TimeVector      = timeVec;
        testResults(t).PositionVector  = posVec;
        testResults(t).VelocityVector  = velVec;
        testResults(t).Status          = test_status;

        % Optional: You could create a figure for each run
        % (Too many figures if you have many test cases, but useful for debugging)
        figure('Name',['Result_' test_cases(t).name],'Visible','off'); 
        subplot(2,1,1);
        plot(timeVec, posVec, 'LineWidth',1.5); grid on;
        xlabel('Time (s)'); ylabel('Position (revolutions)');
        title(['Position: ' test_cases(t).name]);

        subplot(2,1,2);
        plot(timeVec, velVec, 'LineWidth',1.5); grid on;
        xlabel('Time (s)'); ylabel('Velocity (rev/s)');
        title(['Velocity: ' test_cases(t).name]);

        % If you want them visible, remove the 'Visible','off' property
    end

    %% Display Final Summary
    disp('====================================================');
    disp('Test Summary:');
    for t = 1:length(testResults)
        fprintf('%-40s: %s\n', testResults(t).TestName, testResults(t).Status);
    end

    % Optionally save test information and plots:
    % save('StepperSimTestResults.mat','testResults');

    disp('====================================================');
    disp('All test cases completed.');
end