/* Header sensor node
 *
 * Author: Leonardo Bonati
 * Created on Feb. 2018
 *
 */

#include <omnetpp.h>
//#include "common.h"

using namespace omnetpp;

namespace csma_ca {

class SensorNodeCSMACA : public cSimpleModule
{
  private:
    cMessage *backoff_timer_expired;
    cMessage *set_channel_busy[2];
    cMessage *set_channel_free[2];
    cMessage *send_message;
    cMessage *decrease_concurrent_tx_counter[2];
    int nb; // Number of backoffs. If this exceeds macMaxCSMABackoffs, will drop the packets.
    int be; // Maximum backoff time for this backoff cycle. Incremeneted every time a retry takes place.
    int macMinBE;
    int macMaxBE;
    int macMaxCSMABackoffs; // Max number of backoffs that is allowed.
    double D_bp;
    int T;
    double D_p;
    int pkt_to_send;
    int tot_pkt;
    double T_cca;
    double pkt_creation_time;
    double p_tx;
    double p_rx;
    int net;
    simsignal_t sig_avg_delivery_ratio;
    simsignal_t sig_avg_latency;
    simsignal_t sig_latency;
    simsignal_t sig_avg_energy_cons;
    simsignal_t sig_energy_cons;
    simsignal_t sig_pkts_timeout;
    simsignal_t sig_pkts_dropped;
    simsignal_t sig_retries;
    simsignal_t sig_avg_retries;


  public:
    SensorNodeCSMACA();
     virtual ~SensorNodeCSMACA();

  protected:
    virtual void initialize();
    virtual void handleMessage(cMessage *msg);
    virtual void finish();
    bool perform_cca();
    void set_channel_state(bool state, int chan);
    double generate_backoff_time();
    void decrease_and_repeat();
    void setChannelBusy(int chan);
    void setChannelFree(int chan);
};

Define_Module(SensorNodeCSMACA);

}; // namespace
