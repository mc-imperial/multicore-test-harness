filename = "pi_results2.json";
fid = fopen(filename);
raw = fread(fid,inf);
str = char(raw');
fclose(fid);
val_tuning = jsondecode(str);

cache_fuzz_1=val_tuning.cache_fuzz_1;
cache_fuzz_2=val_tuning.cache_fuzz_2;
cache_fuzz_3=val_tuning.cache_fuzz_3;
cache_fuzz_4=val_tuning.cache_fuzz_4;

process_data(cache_fuzz_1);
process_data(cache_fuzz_2);
process_data(cache_fuzz_3);
process_data(cache_fuzz_4);

[times1, q_values1, maximum1, stable_qs1, success1, q_min1, q_max1] = process_data(cache_fuzz_1);
[times2, q_values2, maximum2, stable_qs2, success2, q_min2, q_max2] = process_data(cache_fuzz_2);
[times3, q_values3, maximum3, stable_qs3, success3, q_min3, q_max3] = process_data(cache_fuzz_3);
[times4, q_values4, maximum4, stable_qs4, success4, q_min4, q_max4] = process_data(cache_fuzz_4);

stopping1 = cache_fuzz_1.stopping;
stopping2 = cache_fuzz_2.stopping;
stopping3 = cache_fuzz_3.stopping;
stopping4 = cache_fuzz_4.stopping;



figure(1)
hold on
plot(times1)
plot(times2)
plot(times3)
plot(times4)
title(filename,'Interpreter', 'none')
xlabel('Iterations') 
ylabel('Minutes')
leg = legend(stopping1, stopping2, stopping3, stopping4);
set(leg,'Interpreter', 'none')
hold off

figure(2)
hold on
x1 = 1:length(q_values1);
x2 = 1:length(q_values2);
x3 = 1:length(q_values3);
x4 = 1:length(q_values4);
errorbar(x1, q_values1, q_values1-q_min1, q_max1-q_values1)
errorbar(x2, q_values2, q_values2-q_min2, q_max2-q_values2)
errorbar(x3, q_values3, q_values3-q_min3, q_max3-q_values3)
errorbar(x4, q_values4, q_values4-q_min4, q_max4-q_values4)
title(filename,'Interpreter', 'none')
xlabel('Iterations') 
ylabel('Quantile value')
leg = legend(stopping1, stopping2, stopping3, stopping4);
set(leg,'Interpreter', 'none')
hold off

figure(3)
hold on
plot(maximum1)
plot(maximum2)
plot(maximum3)
plot(maximum4)
title(filename,'Interpreter', 'none')
xlabel('Iterations') 
ylabel('Maximum quantile found')
leg = legend(stopping1, stopping2, stopping3, stopping4);
set(leg,'Interpreter', 'none')
hold off


figure(4)
hold on
plot(stable_qs1)
plot(stable_qs2)
plot(stable_qs3)
plot(stable_qs4)
title(filename,'Interpreter', 'none')
xlabel('Iterations') 
ylabel('Stable q used')
leg = legend(stopping1, stopping2, stopping3, stopping4);
set(leg,'Interpreter', 'none')
hold off

figure(5)
hold on
plot(success1)
plot(success2)
plot(success3)
plot(success4)
title(filename,'Interpreter', 'none')
xlabel('Iterations') 
ylabel('Success')
leg = legend(stopping1, stopping2, stopping3, stopping4);
set(leg,'Interpreter', 'none')
hold off