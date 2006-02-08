/*----------------------------------------------------------------------
$Id: OutputModule.cc,v 1.10 2006/02/03 06:00:15 jbk Exp $
----------------------------------------------------------------------*/

#include <vector>

#include "FWCore/Framework/interface/OutputModule.h"
#include "FWCore/Framework/interface/ConstProductRegistry.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Framework/interface/TriggerNamesService.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventPrincipal.h"
#include "FWCore/Framework/interface/Log.h"
#include "FWCore/Utilities/interface/Exception.h"
#include "FWCore/Utilities/interface/DebugMacros.h"

namespace
{
  // This grotesque little function exists just to allow calling of
  // ConstProductRegistry::allBranchDescriptions in the context of
  // OutputModule's initialization list, rather than in the body of
  // the constructor.

  std::vector<edm::BranchDescription const*>
  getAllBranchDescriptions()
  {
    edm::Service<edm::ConstProductRegistry> reg;
    return reg->allBranchDescriptions();
  }

  std::vector<std::string> getAllTriggerNames()
  {
    edm::Service<edm::service::TriggerNamesService> trig_names;
    std::vector<std::string> names;
    trig_names->getNames(names);
    return names;
  }

}


namespace edm {
  OutputModule::OutputModule(ParameterSet const& pset) : 
    nextID_(), 
    descVec_(),
    process_name_(Service<service::TriggerNamesService>()->getProcessName()),
    groupSelector_(pset,
		   getAllBranchDescriptions()),
    eventSelector_(pset,process_name_,
		   getAllTriggerNames()),
    // use this temporarily - can only apply event selection to current
    // process name
    selectResult_(eventSelector_.getProcessName())
  {
    Service<ConstProductRegistry> reg;
    nextID_ = reg->nextID();

    // TODO: See if we can collapse descVec_ and groupSelector_ into a
    // single object. See the notes in the header for GroupSelector
    // for more information.

    ProductRegistry::ProductList::const_iterator it  = 
      reg->productList().begin();
    ProductRegistry::ProductList::const_iterator end = 
      reg->productList().end();

    for ( ; it != end; ++it)
      {
	if (selected(it->second)) descVec_.push_back(&it->second);
      }
  }

  OutputModule::~OutputModule() { }

  void OutputModule::beginJob(EventSetup const&) { }

  void OutputModule::endJob() { }

  void OutputModule::writeEvent(EventPrincipal const& ep,
				ModuleDescription const& md)
  {
    FDEBUG(2) << "writeEvent called\n";
    if(eventSelector_.wantAll() || wantEvent(ep,md))
      write(ep);
  }

  bool OutputModule::wantEvent(EventPrincipal const& ep,
			       ModuleDescription const& md)
  {
    // this implementation cannot deal with doing event selection
    // based on any previous TriggerResults.  It can only select
    // based on a TriggerResult made in the current process.

    // use module description and const_cast unless interface to
    // event is changed to just take a const EventPrincipal
    Event e(const_cast<EventPrincipal&>(ep),md);
    typedef edm::Handle<edm::TriggerResults> Trig;
    Trig prod;
    e.get(selectResult_,prod);
    bool rc = eventSelector_.acceptEvent(*prod);
	FDEBUG(2) << "Accept event " << ep.id() << " " << rc << "\n";
	FDEBUG(2) << "Mask: " << *prod << "\n";
	return rc;
  }

  bool OutputModule::selected(BranchDescription const& desc) const
  {
    return groupSelector_.selected(desc);
  }

  unsigned long OutputModule::nextID() const 
  {
    return nextID_;
  }
}
