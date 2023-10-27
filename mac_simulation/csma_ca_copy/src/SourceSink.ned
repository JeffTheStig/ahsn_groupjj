// Simulation NED file
//
// Author: Leonardo Bonati
// Created on Feb. 2018
//

package src;

// Sensor node
simple SensorNodeCSMACA
{
    parameters:
        int T_value @unit(s) = default(5.0s);
        double T_cca_value @unit(s) = default(0.000128s);
        double D_bp_value @unit(s) = default(0.00032s);
        int macMinBE_value @prompt("macMinBE") = default(3);
        int macMaxBE_value @prompt("macMaxBE") = default(4);
        int macMaxCSMABackoffs_value @prompt("macMaxCSMABackoffs") = default(2);
        double D_p_value @unit(s) = default(0.004256s);
        int pkt_to_send_value = default(500);
        double p_tx_value @unit(W) = default(0.0495W);
        double p_rx_value @unit(W) = default(0.0564W);
        @display("i=block/source");
    gates:
        output out[];
}

// Sink
simple SinkNodeCSMACA
{
    parameters:
		@signal[sig_collided_net](type="long");
        @statistic[stat_collided_net](title="Total amount of collision (on this channel)"; source="sig_collided_net"; record=vector, stats;interpolationmode=none);
		@signal[sig_pkts_received_net](type="long");
		@statistic[stat_pkts_received_net](title="Total amount of collisions received packets (on this sink) "; source="sig_pkts_received_net"; record=vector, stats;interpolationmode=none);
        @display("i=block/sink");
    gates:
        input in[];
}

// Network
network SourceSink
{
    parameters:
        int n @prompt("Number of nodes") = default(5);
        double latency @mutable = default(0);
        int dropped_pkts @mutable = default(0);
        int received_pkts @mutable = default(0);
        int collided_pkts @mutable = default(0);
        int total_retries @mutable = default(0);
        int tx_pkts @mutable = default(0);
        double energy @mutable = default(0);
        bool channel_free_net0 @mutable = default(true);
        bool channel_free_net1 @mutable = default(true);
        int concurrent_tx_net0 @mutable = default(0);
        int concurrent_tx_net1 @mutable = default(0);
        @signal[sig_avg_delivery_ratio](type="double");
		@statistic[stat_avg_delivery_ratio](title="Average delivery ratio (%)"; source="sig_avg_delivery_ratio"; record=vector, stats;interpolationmode=none);
		@signal[sig_avg_latency](type="double");
		@statistic[stat_avg_latency](title="Average latency (per received package) (ms)"; source="sig_avg_latency"; record=vector, stats;interpolationmode=none);
		@signal[sig_latency](type="double");
		@statistic[stat_latency](title="Total latency (ms)"; source="sig_latency"; record=vector, stats;interpolationmode=none);
		@signal[sig_avg_energy_cons](type="double");
		@statistic[stat_avg_energy_cons](title="Average energy consumption (per received package) (mJ)"; source="sig_avg_energy_cons"; record=vector, stats;interpolationmode=none);
		@signal[sig_energy_cons](type="double");
		@statistic[stat_energy_cons](title="Total energy consumption (mJ)"; source="sig_energy_cons"; record=vector, stats;interpolationmode=none);
		@signal[sig_pkts_received](type="long");
		@statistic[stat_pkts_received](title="Total received packets (on the entire network)"; source="sig_pkts_received"; record=vector, stats;interpolationmode=none);
		@signal[sig_collided](type="long");
		@statistic[stat_collided](title="Total collisions (on the entire network)"; source="sig_collided"; record=vector,stats;interpolationmode=none);
		@signal[sig_pkts_timeout](type="long");
		@statistic[stat_pkts_timeout](title="Total packtes that timed-out (dropped)"; source="sig_pkts_timeout"; record=vector, stats;interpolationmode=none);
		@signal[sig_pkts_dropped](type="long");
		@statistic[stat_pkts_dropped](title="Total dropped packets (dropped due to timeout or collision, on entire network)"; source="sig_pkts_dropped"; record=vector, stats;interpolationmode=none);
		@signal[sig_retries](type="long");
		@statistic[stat_retries](title="Total amount of retries"; source="sig_retries"; record=vector, stats;interpolationmode=none);
		@signal[sig_avg_retries](type="double");
		@statistic[stat_avg_retries](title="Average amount of retries (per received packet)"; source="sig_avg_retries"; record=vector, stats;interpolationmode=none);
    submodules:
        source[(n*2) - 1]: SensorNodeCSMACA;
        sink[2]: SinkNodeCSMACA;
    connections:
        for i=0..n-1 {
            source[i].out++ --> sink[0].in++;
        }
        for i=n-1..((2*n)-2) {
            source[i].out++ --> sink[1].in++;
        }
        source[n-2].out++ --> sink[1].in++;
        source[n-3].out++ --> sink[1].in++;
        source[n].out++ --> sink[0].in++;
        source[n+1].out++ --> sink[0].in++;
}
